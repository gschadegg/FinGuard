import pytest
import asyncio
from datetime import date as DateType

from app.services.fraud_detection_service import FraudDetectionService
import app.services.fraud_detection_service as svc_mod


class _MockAsyncSession:
    def __init__(self):
        self.commits = 0
        self.exec_calls = []

    async def __aenter__(self):
        return self

    async def __aexit__(self, _exc_type, _exc, _tb):
        return False

    async def commit(self):
        self.commits += 1

    async def execute(self, *args, **kwargs):
        self.exec_calls.append((args, kwargs))
        class _Response:
            pass
        return _Response()


class _MockSessionFactory:
    def __call__(self):
        return _MockAsyncSession()




class MockTransactionRepo:
    def __init__(self, db):
        self.db = db
        self.fetch_calls = []
        self.set_results_calls = []
        self.rows_queue = []

    async def fetch_transactions_for_ML_Model(self, ids):
        self.fetch_calls.append(list(ids))
        return self.rows_queue.pop(0) if self.rows_queue else []

    async def set_fraud_results(self, updates):
        self.set_results_calls.append(list(updates))




def row(txn_id, amount, channel, pending, txn_date, merchant):
    return (txn_id, amount, channel, pending, txn_date, merchant)

@pytest.fixture
def session_factory():
    return _MockSessionFactory()


@pytest.fixture
def monkeypatch_sqlrepo(monkeypatch):

    # need the repo setup in the actual service
    monkeypatch.setattr(
        "app.services.fraud_detection_service.SqlTransactionRepo",
        MockTransactionRepo
    )


@pytest.fixture
def mock_prediction(monkeypatch):
    calls = {"load_count": 0, "predict_inputs": []}

    def _mock_load_pipeline(model_path):
        calls["load_count"] += 1
        return {"feature_state": "stub_state"}, {"models": "stub_model"}

    def _mock_predict_single(features, feature_state, models):
        calls["predict_inputs"].append(dict(features))

        amount = float(features.get("amount", 0.0))
        is_suspected = amount > 100.0

        risk_tier = "HIGH" if amount > 1000 else ("MEDIUM" if amount > 100 else "LOW")
        prediction_score = 0.9 if risk_tier == "HIGH" else (0.6 if risk_tier == "MEDIUM" else 0.1)
        return prediction_score, is_suspected, risk_tier


    # need to mock the funcs in the actual service 
    monkeypatch.setattr("app.services.fraud_detection_service.load_pipeline", _mock_load_pipeline)
    monkeypatch.setattr("app.services.fraud_detection_service.predict_single", _mock_predict_single)
    return calls




@pytest.fixture
def svc(session_factory, monkeypatch_sqlrepo, mock_prediction):
    return FraudDetectionService(
        session_factory=session_factory,
        model_path="fraud_detection/fraud_model.joblib",
        enabled=True
    )



############################
# _run_prediction Tests
############################

# TC-FRAUD-PREDICT-001: Base scenario, processes rows of transactions and set update results
@pytest.mark.anyio
async def test_run_prediction_base(svc, session_factory, mock_prediction):
    mock_session = session_factory()
    svc.session_factory = lambda: mock_session

    repo = MockTransactionRepo(mock_session)
    repo.rows_queue.append([
        row(1, 15.0, "online", False, DateType(2025, 1, 2), "Uber"),
        row(2, 250.0, "in_store", True, DateType(2025, 1, 3), "Electronics"),
    ])

    orig_repo = svc_mod.SqlTransactionRepo
    svc_mod.SqlTransactionRepo = lambda _db: repo 
    try:
        await svc._run_prediction([1, 2])

        assert mock_prediction["load_count"] == 1

        assert repo.fetch_calls == [[1, 2]]
        assert len(repo.set_results_calls) == 1
        updates = repo.set_results_calls[0]
        assert len(updates) == 2

        assert updates[0][0] == 1 and updates[0][2] is False and updates[0][3] == "LOW"
        assert updates[1][0] == 2 and updates[1][2] is True and updates[1][3] == "MEDIUM"

        assert mock_session.commits == 1

        feats = mock_prediction["predict_inputs"]
        assert feats[0]["amount"] == 15.0 and feats[0]["merchant_name"] == "Uber"
        assert feats[1]["amount"] == 250.0 and feats[1]["payment_channel"] == "in_store"
    finally:
        svc_mod.SqlTransactionRepo = orig_repo


# TC-FRAUD-PREDICT-002: maps features
@pytest.mark.anyio
async def test_run_prediction_feature_mapped(svc, session_factory, mock_prediction):
    mock_session = session_factory()
    svc.session_factory = lambda: mock_session

    repo = MockTransactionRepo(mock_session)
    repo.rows_queue.append([
        row(10, 0.0, None, 0, DateType(2025, 2, 1), None),
        row(11, 1200.0, "online", 1, "2025-02-02", "Merchant1"),
        row(12, 85.5, "other", False, None, "Merchant2"),
    ])

    orig_repo = svc_mod.SqlTransactionRepo
    svc_mod.SqlTransactionRepo = lambda _db: repo

    try:
        await svc._run_prediction([10, 11, 12])

        assert mock_prediction["load_count"] == 1

        updates = repo.set_results_calls[0]
        assert [update[0] for update in updates] == [10, 11, 12]

        tiers = [update[3] for update in updates]
        assert tiers == ["LOW", "HIGH", "LOW"]

        feats = mock_prediction["predict_inputs"]
        assert feats[0]["date"] == "2025-02-01"
        assert feats[1]["date"] == "2025-02-02"
        assert feats[2]["date"] is None
    finally:
        svc_mod.SqlTransactionRepo = orig_repo


# TC-FRAUD-PREDICT-003: model is already loaded and isn't reloaded
@pytest.mark.anyio
async def test_run_prediction_model_loaded(svc, session_factory, mock_prediction):
    mock_session = session_factory()
    svc.session_factory = lambda: mock_session

    repo = MockTransactionRepo(mock_session)
    repo.rows_queue.append([row(1, 10.0, "online", False, DateType(2025, 1, 1), "Merchant1")])
    repo.rows_queue.append([row(2, 10.0, "online", False, DateType(2025, 1, 1), "Merchant2")])

    orig_repo = svc_mod.SqlTransactionRepo
    svc_mod.SqlTransactionRepo = lambda _db: repo


    try:
        await svc._run_prediction([1])
        await svc._run_prediction([2])
        assert mock_prediction["load_count"] == 1
    finally:
        svc_mod.SqlTransactionRepo = orig_repo


# TC-FRAUD-PREDICT-004: no found transactions to update
@pytest.mark.anyio
async def test_run_prediction_no_rows(svc, session_factory, mock_prediction):
    mock_session = session_factory()
    svc.session_factory = lambda: mock_session

    repo = MockTransactionRepo(mock_session)
    repo.rows_queue.append([])

    orig_repo = svc_mod.SqlTransactionRepo
    svc_mod.SqlTransactionRepo = lambda _db: repo
    try:
        await svc._run_prediction([999])
        assert mock_prediction["load_count"] == 1
        assert repo.fetch_calls == [[999]]
        assert repo.set_results_calls == [[]]
        assert mock_session.commits == 1
    finally:
        svc_mod.SqlTransactionRepo = orig_repo




############################
# enqueue_ids Tests
############################

# TC-FRAUD-ENQUEUE-001: base scenario, task is scheduled
def test_enqueue_ids_base(monkeypatch, svc):
    scheduled = []

    def _mock_create_task(id):
        scheduled.append(id)
        try:
            id.close()
        except Exception:
            pass

        class _Response:
            pass
        return _Response()

    monkeypatch.setattr(asyncio, "create_task", _mock_create_task)

    # should deduplicate if same ids and just create 1 task
    svc.enqueue_ids([1, "2", 2, 1])

    assert len(scheduled) == 1



# TC-FRAUD-ENQUEUE-002: No tasks scheduled if disabled
def test_enqueue_ids_disabled(monkeypatch, session_factory, mock_prediction):
    svc = FraudDetectionService(
        session_factory=session_factory,
        model_path="fraud_detection/fraud_model.joblib",
        enabled=False
    )

    scheduled = []

    def _mock_create_task(ids):
        scheduled.append(ids)

    monkeypatch.setattr(asyncio, "create_task", _mock_create_task)

    svc.enqueue_ids([1, 2, 3])
    assert scheduled == []


# TC-FRAUD-ENQUEUE-003: No tasks scheduled if empty ids list
def test_enqueue_ids_empty_list(monkeypatch, svc):
    scheduled = []
    monkeypatch.setattr(asyncio, "create_task", lambda c: scheduled.append(c))
    svc.enqueue_ids([])
    svc.enqueue_ids(None)
    assert scheduled == []
