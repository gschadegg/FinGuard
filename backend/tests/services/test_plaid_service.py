import pytest
from typing import List, Optional
from types import SimpleNamespace
from unittest.mock import Mock, AsyncMock
from app.services.plaid_service import PlaidService
from app.domain.entities import UserEntity, ConnectionItemEntity
from fastapi import HTTPException

institution_helper = lambda _id, _name: SimpleNamespace(id=_id, name=_name)

class MockAccountRepo:
    def __init__(self):
        self.rows: List[UserEntity] = []
        self.return_value = [{"id": 1, "name": "Checking", "plaid_account_id": "account_1"}]
        self.calls = []
    
    async def upsert_selected(self, item_id, selected_accounts, institution_id, institution_name, unselect_others=False,):
        self.calls.append({"item_id": item_id, "count": len(list(selected_accounts)), "unselect_others": unselect_others, institution_id: "bank ID", institution_name: "bank Name"})
        return self.return_value
    

class MockConnectionItemRepo:
    def __init__(self, existing=None):
        self.items_by_plaid_id: dict[str, ConnectionItemEntity] = {}
        self.single_item: ConnectionItemEntity = None

        self.get_by_id_calls = 0
        self.add_calls = 0
        self.update_calls = 0
        self.existing = existing

    async def get_by_connection_item_id(self, plaid_item_id: str):
        return self.items_by_plaid_id.get(plaid_item_id)
    
    async def get_by_id(self, id: int) -> Optional[ConnectionItemEntity]:
        self.get_by_id_calls += 1
        return self.single_item
    
    async def add(self, item: ConnectionItemEntity) -> ConnectionItemEntity:
        self.add_calls += 1
        return ConnectionItemEntity(
            id=42,
            user_id=item.user_id,
            plaid_item_id=item.plaid_item_id,
            access_token_encrypted=item.access_token_encrypted,
            institution_id=item.institution_id,
            institution_name=item.institution_name,
            accounts=[],
        )

    async def update(self, item_or_entity, token_encrypted, institution_id, institution_name) -> ConnectionItemEntity:
        self.update_calls += 1
        return ConnectionItemEntity(
            id=(item_or_entity.id if isinstance(item_or_entity, ConnectionItemEntity) else 99),
            user_id=123,
            plaid_item_id="item-updated",
            access_token_encrypted=token_encrypted,
            institution_id=institution_id,
            institution_name=institution_name,
            accounts=[],
        )

# mocking plaid models
class MockAccountsGetRequestOptions:
    def __init__(self, account_ids: Optional[List[str]] = None):
        self.account_ids = account_ids

class MockAccountsGetRequest:
    def __init__(self, access_token: str, options: Optional[MockAccountsGetRequestOptions] = None):
        self.access_token = access_token
        self.options = options

class MockTransactionsSyncRequest:
        def __init__(self, **kwargs):
            self.kwargs = kwargs
## 


class ApiException(Exception):
    def __init__(self, status, body):
        self.status = status
        self.body = body

def _transaction_sync_resp(added=None, modified=None, removed=None, next_cursor=None, has_more=False):
    return SimpleNamespace(
        to_dict=lambda: {
            "added": added or [],
            "modified": modified or [],
            "removed": removed or [],
            "next_cursor": next_cursor,
            "has_more": has_more,
        }
    )


@pytest.fixture
def mock_plaid_models(monkeypatch):
    monkeypatch.setattr("app.services.plaid_service.AccountsGetRequest", MockAccountsGetRequest, raising=False)
    monkeypatch.setattr("app.services.plaid_service.AccountsGetRequestOptions", MockAccountsGetRequestOptions, raising=False)
    monkeypatch.setattr("app.services.plaid_service.TransactionsSyncRequest", MockTransactionsSyncRequest, raising=False)

def _plaid_resp(accounts: List[dict]) -> SimpleNamespace:
    return SimpleNamespace(to_dict=lambda: {"accounts": accounts})

@pytest.fixture
def mock_plaid_client(monkeypatch):
    client = SimpleNamespace(
        link_token_create=Mock(name="link_token_create"),
        item_public_token_exchange=Mock(name="item_public_token_exchange"),
        accounts_get=Mock(name="accounts_get"),
        transactions_sync=Mock(name="transactions_sync")
    )

    monkeypatch.setattr("app.services.plaid_service.plaid_client", client)
    monkeypatch.setattr("app.services.plaid_service.encrypt", lambda s: "encrypt-access-token")
    monkeypatch.setattr("app.services.plaid_service.decrypt", lambda s: "decrypted-access-token")
    monkeypatch.setattr("app.services.plaid_service.plaid", SimpleNamespace(ApiException=ApiException))
    return client




############################
# create_link_token Tests
############################


# Test Case TC-PLAID-LINK-001: create_link_token BASE scenario
@pytest.mark.anyio
async def test_create_link_token_base(mock_plaid_client):
    svc = PlaidService(account_repo=MockAccountRepo(), connection_item_repo=MockConnectionItemRepo()) 

    mock_plaid_client.link_token_create.return_value = SimpleNamespace(
        to_dict=lambda: {"link_token": "link-token-sandbox-123"}
    )

    result = await svc.create_link_token(user_id=123)

    assert result == {"ok": True, "link_token": "link-token-sandbox-123", "mode": "create"} 
    assert mock_plaid_client.link_token_create.call_count == 1



# Test Case TC-PLAID-LINK-002: create_link_token Plaid throws error scenario
@pytest.mark.anyio
async def test_create_link_token_plaid_error(mock_plaid_client):
    svc = PlaidService(account_repo=MockAccountRepo(), connection_item_repo=MockConnectionItemRepo()) 

    mock_plaid_client.link_token_create.side_effect = RuntimeError("Plaid Error")

    with pytest.raises(HTTPException) as ei:
        await svc.create_link_token(user_id=123)

    assert ei.value.status_code == 500

# Test Case TC-PLAID-LINK-003: update mode with existing item found, returns update link token
@pytest.mark.anyio
async def test_create_link_token_update_success(mock_plaid_client):
    connectionItem_repo = MockConnectionItemRepo()

    existing = ConnectionItemEntity(
        id=1, user_id=123, plaid_item_id="item-123",
        access_token_encrypted="encrypted", institution_id=None, institution_name=None, accounts=[]
    )
    connectionItem_repo.items_by_plaid_id["item-123"] = existing

    svc = PlaidService(account_repo=MockAccountRepo(), connection_item_repo=connectionItem_repo)

    mock_plaid_client.link_token_create.return_value = SimpleNamespace(
        to_dict=lambda: {"link_token": "link-token-update-123"}
    )

    result = await svc.create_link_token(user_id=123, mode="update", plaid_item_id="item-123")

    assert result["ok"] is True
    assert result["mode"] == "update"
    assert result["plaid_item_id"] == "item-123"
    assert result["link_token"] == "link-token-update-123"
    assert mock_plaid_client.link_token_create.call_count == 1


# Test Case TC-PLAID-LINK-004: update mode where item is not found and returns 404
@pytest.mark.anyio
async def test_create_link_token_update_not_found(mock_plaid_client):
    connectionItem_repo = MockConnectionItemRepo() 
    svc = PlaidService(account_repo=MockAccountRepo(), connection_item_repo=connectionItem_repo)

    with pytest.raises(HTTPException) as ei:
        await svc.create_link_token(user_id=123, mode="update", plaid_item_id="missing-item")

    assert ei.value.status_code == 404


############################
# exchange_public_token Tests
############################

# Test Case TC-PLAID-TOKEN-001: BASE scenario creates connection item
@pytest.mark.anyio
async def test_exchange_public_token_base(mock_plaid_client):
    mock_plaid_client.item_public_token_exchange.return_value = SimpleNamespace(
        to_dict=lambda: {"access_token": "access_token-123", "item_id": "item-123"}
    )
    account_repo = MockAccountRepo()
    connectionItem_repo = MockConnectionItemRepo(existing=None)
    svc = PlaidService(account_repo, connectionItem_repo)

    result = await svc.exchange_public_token(
        public_token="public-token",
        user_id=7,
        selected_accounts=[{"id": "account_1", "name": "Checking"}],
        institution=institution_helper("institution1", "Chase"),
        unselect_others=True,
    )

    assert result["ok"] is True
    assert result["mode"] == "created"
    assert result["plaid_item_id"] == "item-123"
    assert result["connection_item_id"] == 42
    assert result["institution"] == {"id": "institution1", "name": "Chase"}

    assert connectionItem_repo.add_calls == 1
    assert connectionItem_repo.update_calls == 0
    assert len(account_repo.calls) == 1

    assert account_repo.calls[0]["item_id"] == 42
    assert account_repo.calls[0]["unselect_others"] is True


# Test Case TC-PLAID-TOKEN-002: no public_token, throws 400, no collaborator calls
@pytest.mark.anyio
async def test_exchange_public_token_missing_public_token(mock_plaid_client):
    account_repo = MockAccountRepo()
    connectionItem_repo = MockConnectionItemRepo()
    svc = PlaidService(account_repo, connectionItem_repo)

    with pytest.raises(HTTPException) as ei:
        await svc.exchange_public_token(
            public_token="",
            user_id=7,
            selected_accounts=[],
            institution=None,
        )
    assert ei.value.status_code == 400
    assert "public_token is required" in ei.value.detail
    assert mock_plaid_client.item_public_token_exchange.call_count == 0


# Test Case TC-PLAID-TOKEN-003: Plaid throws error, raises exception
@pytest.mark.anyio
async def test_exchange_public_token_plaid_throws(mock_plaid_client, monkeypatch):
    # class ApiException(Exception):
    #     def __init__(self, status, body):
    #         self.status = status
    #         self.body = body
    monkeypatch.setattr("app.services.plaid_service.plaid", SimpleNamespace(ApiException=ApiException))
    mock_plaid_client.item_public_token_exchange.side_effect = ApiException(503, '{"error":"upstream"}')

    svc = PlaidService(MockAccountRepo(), MockConnectionItemRepo())

    with pytest.raises(HTTPException) as ei:
        await svc.exchange_public_token(public_token="public_token", user_id=1)
    assert ei.value.status_code == 503
    assert mock_plaid_client.item_public_token_exchange.call_count == 1


# Test Case TC-PLAID-TOKEN-004: found existing item, update path (no add), 200
@pytest.mark.anyio
async def test_exchange_public_token_update_existing(mock_plaid_client):
    mock_plaid_client.item_public_token_exchange.return_value = SimpleNamespace(
        to_dict=lambda: {"access_token": "access_token-123", "item_id": "item-123"}
    )
    existing = ConnectionItemEntity(
        id=9, user_id=1, plaid_item_id="item-123",
        access_token_encrypted="encrypted-old", institution_id=None, institution_name=None, accounts=[]
    )
    account_repo = MockAccountRepo()
    connectionItem_repo = MockConnectionItemRepo(existing=existing)
    connectionItem_repo.items_by_plaid_id["item-123"] = existing 

    svc = PlaidService(account_repo, connectionItem_repo)

    result = await svc.exchange_public_token(
        public_token="public_token",
        user_id=1,
        selected_accounts=[{"id": "account_1"}],
        institution=institution_helper("institution2", "Another Bank"),
        unselect_others=False,
    )

    assert result["ok"] is True
    assert result["mode"] == "updated"
    assert result["plaid_item_id"] == "item-123"
    assert result["connection_item_id"] == 9
    assert connectionItem_repo.update_calls == 1
    assert connectionItem_repo.add_calls == 0
    assert len(account_repo.calls) == 1
    assert account_repo.calls[0]["unselect_others"] is False


# Test Case TC-PLAID-TOKEN-005: no added accounts, upsert not called, connection created
@pytest.mark.anyio
async def test_exchange_public_token_no_selected_accounts(mock_plaid_client):
    mock_plaid_client.item_public_token_exchange.return_value = SimpleNamespace(
        to_dict=lambda: {"access_token": "access_token-123", "item_id": "item-123"}
    )
    account_repo = MockAccountRepo()
    connectionItem_repo = MockConnectionItemRepo(existing=None)
    svc = PlaidService(account_repo, connectionItem_repo)

    result = await svc.exchange_public_token(public_token="public_token", user_id=1, selected_accounts=None)

    assert result["ok"] is True
    assert result["mode"] == "created"
    assert len(account_repo.calls) == 0 


# Test Case TC-PLAID-TOKEN-006: database fails to add connection item
@pytest.mark.anyio
async def test_exchange_public_token_add_fails(mock_plaid_client, monkeypatch):
    mock_plaid_client.item_public_token_exchange.return_value = SimpleNamespace(
        to_dict=lambda: {"access_token": "access_token-123", "item_id": "item-123"}
    )

    class FailingConnectionRepo(MockConnectionItemRepo):
        async def add(self, item):
            raise RuntimeError("database add failed")

    svc = PlaidService(MockAccountRepo(), FailingConnectionRepo(existing=None))

    with pytest.raises(RuntimeError) as ei:
        await svc.exchange_public_token(public_token="public_token", user_id=1, selected_accounts=[])
    assert "database add failed" in str(ei.value)


# Test Case TC-PLAID-TOKEN-007: database fails to update, account upsert not called
@pytest.mark.anyio
async def test_exchange_public_token_update_fails(mock_plaid_client):
    mock_plaid_client.item_public_token_exchange.return_value = SimpleNamespace(
        to_dict=lambda: {"access_token": "access_token-123", "item_id": "item-123"}
    )
    existing = ConnectionItemEntity(
        id=5, user_id=1, plaid_item_id="item-123",
        access_token_encrypted="encrypt-old", institution_id=None, institution_name=None, accounts=[]
    )

    class FailingConnRepo(MockConnectionItemRepo):
        async def update(self, *args, **kwargs):
            raise RuntimeError("db update failed")

    account_repo = MockAccountRepo()
    connectionItem_repo = FailingConnRepo(existing=existing)
    connectionItem_repo.items_by_plaid_id["item-123"] = existing 
    
    svc = PlaidService(account_repo, connectionItem_repo)

    with pytest.raises(RuntimeError):
        await svc.exchange_public_token(public_token="public_token", user_id=1, selected_accounts=[{"id": "account_1"}])
    assert len(account_repo.calls) == 0 


# Test Case TC-PLAID-TOKEN-008: encrypt func fails, raise exception, no  db repo calls
@pytest.mark.anyio
async def test_exchange_public_token_encrypt_fails(mock_plaid_client, monkeypatch):
    mock_plaid_client.item_public_token_exchange.return_value = SimpleNamespace(
        to_dict=lambda: {"access_token": "access_token-123", "item_id": "item-123"}
    )
    # make encrypt throw
    monkeypatch.setattr("app.services.plaid_service.encrypt", lambda s: (_ for _ in ()).throw(RuntimeError("enc failed")))

    account_repo = MockAccountRepo()
    connectionItem_repo = MockConnectionItemRepo(existing=None)
    svc = PlaidService(account_repo, connectionItem_repo)

    with pytest.raises(RuntimeError):
        await svc.exchange_public_token(public_token="public_token", user_id=1, selected_accounts=[])
    assert connectionItem_repo.add_calls == 0
    assert connectionItem_repo.update_calls == 0
    assert len(account_repo.calls) == 0


# Test Case TC-PLAID-TOKEN-009: public_token already used, Plaid sends 400
@pytest.mark.anyio
async def test_exchange_public_token_plaid_400_used_token(mock_plaid_client, monkeypatch):
    class ApiException(Exception):
        def __init__(self, status, body):
            self.status = status
            self.body = body
    monkeypatch.setattr("app.services.plaid_service.plaid", SimpleNamespace(ApiException=ApiException))

    mock_plaid_client.item_public_token_exchange.side_effect = ApiException(400, '{"error":"PUBLIC_TOKEN_INVALID"}')

    svc = PlaidService(MockAccountRepo(), MockConnectionItemRepo())
    with pytest.raises(HTTPException) as ei:
        await svc.exchange_public_token(public_token="used", user_id=1)
    assert ei.value.status_code == 400
    assert mock_plaid_client.item_public_token_exchange.call_count == 1



############################
# get_accounts Tests
############################


# TC-PLAID-ACCTS-001: BASE scenario, accounts details returned
@pytest.mark.anyio
async def test_get_accounts_base(mock_plaid_client, mock_plaid_models):
    svc = PlaidService(account_repo=MockAccountRepo(), connection_item_repo=MockConnectionItemRepo())

    mock_plaid_client.accounts_get.return_value = _plaid_resp([
        {"account_id": "account_1", "name": "Checking"},
        {"account_id": "account_2", "name": "Savings"},
    ])

    out = await svc.get_accounts(access_token="token-123")
    assert set(out.keys()) == {"account_1", "account_2"}
    assert mock_plaid_client.accounts_get.call_count == 1

    (req,), _ = mock_plaid_client.accounts_get.call_args

    assert isinstance(req, MockAccountsGetRequest)
    assert req.access_token == "token-123"
    assert req.options is None


# TC-PLAID-ACCTS-002: Filtered for only requested accounts
@pytest.mark.anyio
async def test_get_accounts_filtered(mock_plaid_client, mock_plaid_models):
    svc = PlaidService(account_repo=MockAccountRepo(), connection_item_repo=MockConnectionItemRepo())

    mock_plaid_client.accounts_get.return_value = _plaid_resp([
        {"account_id": "account_2", "name": "Savings"},
    ])

    out = await svc.get_accounts(access_token="token-123", account_ids=["account_2"])
    assert set(out.keys()) == {"account_2"}

    (req,), _ = mock_plaid_client.accounts_get.call_args
    assert isinstance(req.options, MockAccountsGetRequestOptions)
    assert req.options.account_ids == ["account_2"]


# TC-PLAID-ACCTS-003: Get account access token from item_id
@pytest.mark.anyio
async def test_get_accounts_by_item_id(mock_plaid_client, mock_plaid_models):
    repo = MockConnectionItemRepo()
    repo.single_item = ConnectionItemEntity(
        id=42, user_id=1, plaid_item_id="item-abc",
        access_token_encrypted="ENCRYPTED-XYZ",
        institution_id="ins_3", institution_name="Chase", accounts=[]
    )
    svc = PlaidService(account_repo=MockAccountRepo(), connection_item_repo=repo)

    mock_plaid_client.accounts_get.return_value = _plaid_resp([
        {"account_id": "account_1", "name": "Checking"},
    ])

    out = await svc.get_accounts(item_id=42, account_ids=["account_1"])
    assert set(out.keys()) == {"account_1"}

    (req,), _ = mock_plaid_client.accounts_get.call_args

    assert req.access_token == "decrypted-access-token"
    assert isinstance(req.options, MockAccountsGetRequestOptions)
    assert req.options.account_ids == ["account_1"]


# TC-PLAID-ACCTS-004: Both access token and item_id params missing, throws exception
@pytest.mark.anyio
async def test_get_accounts_missing_params(mock_plaid_client, mock_plaid_models):
    svc = PlaidService(account_repo=MockAccountRepo(), connection_item_repo=MockConnectionItemRepo())
    with pytest.raises(ValueError) as ei:
        await svc.get_accounts()
    assert "Provide either Access Token or Connection ID" in str(ei.value)


# TC-PLAID-ACCTS-005: item_id not found, returns {}
@pytest.mark.anyio
async def test_get_accounts_not_found(mock_plaid_client, mock_plaid_models):
    repo = MockConnectionItemRepo()
    repo.single_item = None
    svc = PlaidService(account_repo=MockAccountRepo(), connection_item_repo=repo)

    out = await svc.get_accounts(item_id=999)
    assert out == {}
    assert mock_plaid_client.accounts_get.call_count == 0  # no plaid call


# TC-PLAID-ACCTS-006: Plaid throws exception, returns {}
@pytest.mark.anyio
async def test_get_accounts_plaid_error(mock_plaid_client, mock_plaid_models, monkeypatch):
    svc = PlaidService(account_repo=MockAccountRepo(), connection_item_repo=MockConnectionItemRepo())

    def error_thrown(_req):
        raise ApiException(status=400, body="bad")
    mock_plaid_client.accounts_get.side_effect = error_thrown

    out = await svc.get_accounts(access_token="token-123", account_ids=["account_1"])
    assert out == {}



############################
# transactions_sync Tests
############################

# TC-PLAID-SYNC-001: BASE scenario and initial sync
@pytest.mark.anyio
async def test_transactions_sync_base_no_cursor(mock_plaid_client, mock_plaid_models):
    svc = PlaidService(account_repo=MockAccountRepo(), connection_item_repo=MockConnectionItemRepo())

    mock_plaid_client.transactions_sync.return_value = _transaction_sync_resp(
        added=[{"transaction_id": "transaction_1"}],
        modified=[],
        removed=[],
        next_cursor="cursor-1",
        has_more=False,
    )

    out = await svc.transactions_sync(access_token="access_token", cursor=None)

    assert out == {
        "added": [{"transaction_id": "transaction_1"}],
        "modified": [],
        "removed": [],
        "next_cursor": "cursor-1",
        "has_more": False,
    }

    assert mock_plaid_client.transactions_sync.call_count == 1


    req = mock_plaid_client.transactions_sync.call_args[0][0]
    assert req.kwargs["access_token"] == "access_token"
    assert req.kwargs["count"] == 500
    
    assert "cursor" not in req.kwargs


# TC-PLAID-SYNC-002: Cursor exists, updates cursor on next sync
@pytest.mark.anyio
async def test_transactions_sync_with_cursor(mock_plaid_client, mock_plaid_models):
    svc = PlaidService(account_repo=MockAccountRepo(), connection_item_repo=MockConnectionItemRepo())

    mock_plaid_client.transactions_sync.return_value = _transaction_sync_resp(
        added=[],
        modified=[{"transaction_id": "transaction_2"}],
        removed=[],
        next_cursor="cursor-2",
        has_more=True,
    )

    out = await svc.transactions_sync(access_token="access_token", cursor="cursor-0")

    assert out["modified"] == [{"transaction_id": "transaction_2"}]
    assert out["next_cursor"] == "cursor-2"
    assert out["has_more"] is True

    req = mock_plaid_client.transactions_sync.call_args[0][0]
    assert req.kwargs["access_token"] == "access_token"
    assert req.kwargs["cursor"] == "cursor-0" 
    assert req.kwargs["count"] == 500


# TC-PLAID-SYNC-003: Plaid throws exception
@pytest.mark.anyio
async def test_transactions_sync_plaid_exception(mock_plaid_client, mock_plaid_models):
    svc = PlaidService(account_repo=MockAccountRepo(), connection_item_repo=MockConnectionItemRepo())


    mock_plaid_client.transactions_sync.side_effect = ApiException(500, "error thrown")

    out = await svc.transactions_sync(access_token="access_token", cursor="cursor-1")

    assert out == {
        "added": [],
        "modified": [],
        "removed": [],
        "next_cursor": "cursor-1",
        "has_more": False,
    }


# TC-PLAID-SYNC-004: Check for missing TransactionSyncRequest Model
@pytest.mark.anyio
async def test_transactions_sync_model_missing(monkeypatch, mock_plaid_client):

    monkeypatch.setattr("app.services.plaid_service.TransactionsSyncRequest", None, raising=False)

    svc = PlaidService(account_repo=MockAccountRepo(), connection_item_repo=MockConnectionItemRepo())
    out = await svc.transactions_sync(access_token="access_token", cursor="cursor-2")


    assert mock_plaid_client.transactions_sync.call_count == 0
    assert out == {
        "added": [],
        "modified": [],
        "removed": [],
        "next_cursor": "cursor-2",
        "has_more": False,
    }