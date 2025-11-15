import pytest
from types import SimpleNamespace
from decimal import Decimal
from datetime import date as real_date

from app.services.dashboard_service import DashboardService
from app.domain.entities import DashboardEntity

class MockAccountService:
    def __init__(self):
        self.accounts_to_return = []

        self.list_calls = []

    async def list_all_user_accounts(self, user_id, selected):
        self.list_calls.append({"user_id": user_id, "selected": selected})
        return self.accounts_to_return


class MockBudgetService:
    def __init__(self):
        self.budget_to_return = None
        self.calls = []

    async def list_categories(self, user_id: int, year: int, month: int):

        self.calls.append({"user_id": user_id, "year": year, "month": month})
        return self.budget_to_return


class MockTransactionService:
    def __init__(self):
        self.rollups_to_return = {}
        self.calls = []

    async def get_rollups(self, user_id: int):

        self.calls.append({"user_id": user_id})
        return self.rollups_to_return


def create_account(
    *,
    id: int,
    inst_name: str = "Bank",
    current: Decimal | float | int | None = None,
    available: Decimal | float | int | None = None,
    name: str = "Account",
    mask: str = "0000",
    type_: str = "depository",
    subtype: str = "checking",
    selected: bool = True,
):

    balances = None
    if current is not None or available is not None:
        balances = SimpleNamespace(
            current=current,
            available=available,
        )

    plaid = SimpleNamespace(
        name=name,
        mask=mask,
        balances=balances,
    )

    return SimpleNamespace(
        id=id,
        name=name,
        mask=mask,
        type=type_,
        subtype=subtype,
        institution_name=inst_name,
        selected=selected,
        plaid=plaid,
    )

@pytest.fixture
def svc(monkeypatch):
    account_svc = MockAccountService()
    budget_svc = MockBudgetService()
    transaction_svc = MockTransactionService()

    svc = DashboardService(account_svc=account_svc, budget_svc=budget_svc,transaction_svc=transaction_svc, )

    return svc

############################
# get_dashboard Tests
############################

# TC-DASH-001: base scenario with complete data
@pytest.mark.anyio
async def test_get_dashboard_base(svc):

    # adding mock accounts
    svc.account_svc.accounts_to_return = [
        create_account(id=1, inst_name="Bank 1", current=Decimal("100.00"), available=Decimal("90.00"), name="Checking A"),
        create_account(id=2, inst_name="Bank 2", current=Decimal("200.00"), available=Decimal("190.00"), name="Savings B"),
    ]

    # adding budget data
    svc.budget_svc.budget_to_return = {
        "categories": [
            {
                "id": 1,
                "name": "Rent",
                "allotted_amount": Decimal("500.00"),
                "group": "Expenses",
                "spent_amount": "200.00",
                "remaining_amount": "300.00",
            },
            {
                "id": 2,
                "name": "Movies",
                "allotted_amount": Decimal("45.00"),
                "group": "Entertainment",
                "spent_amount": "20.00",
                "remaining_amount": "25.00",
            },
        ],
        "total_budgeted": "545.00",
        "total_spent": "220.00",
        "total_remaining": "325.00",
        "period": {"start_date": "2025-11-01", "end_date": "2025-12-01"},
    }

    #adding mock risk data
    svc.transaction_svc.rollups_to_return = {
        "risks": {
            "pending_total": 4,
            "pending_high": 4,
            "pending_medium": 0,
            "pending_low": 0,
        },
        "by_account": {},
    }

    out = await svc.get_dashboard(
        user_id=123,
        year=2025,
        month=11,
    )

    # making sure services were called
    assert svc.account_svc.list_calls == [{"user_id": 123, "selected": True}]
    assert svc.budget_svc.calls == [{"user_id": 123, "year": 2025, "month": 11}]
    assert svc.transaction_svc.calls == [{"user_id": 123}]

    # check period data
    assert out.period["year"] == 2025
    assert out.period["month"] == 11

    assert out.period["label"] == "November 2025"

    # check totals
    assert out.totals == Decimal("300.00")

    # check risk data shows up
    assert out.risk_data["risks"]["pending_high"] == 4

    # check that the budget data is calc
    assert out.budget.budget == Decimal("545.00")
    assert out.budget.spent == Decimal("220.00")
    assert out.budget.available == Decimal("325.00")


    assert len(out.spending_categories) == 2
    names = {category.name for category in out.spending_categories}
    assert names == {"Rent", "Movies"}


    rent_slice = next(category for category in out.spending_categories if category.name == "Rent")
    movies_slice = next(category for category in out.spending_categories if category.name == "Movies")

    # check that the category slices has proper amoutns and percentages calc
    assert rent_slice.amount == Decimal("200.00")
    assert movies_slice.amount == Decimal("20.00")
    assert rent_slice.percent == pytest.approx(90.9, rel=1e-3)
    assert movies_slice.percent == pytest.approx(9.09, rel=1e-3)

    # check that the accounts flatten and data is present
    assert len(out.accounts) == 2
    assert out.accounts[0].institution_name == "Bank 1"
    assert out.accounts[1].institution_name == "Bank 2"


# TC-DASH-002: No accounts are connected & no budget
@pytest.mark.anyio
async def test_get_dashboard_no_accounts_or_budget(svc):
    svc.account_svc.accounts_to_return = []

    svc.budget_svc.budget_to_return = {
        "categories": [],
        "total_budgeted": "0",
        "total_spent": "0",
        "total_remaining": "0",
        "period": {"start_date": "2025-11-01", "end_date": "2025-12-01"},
    }

    svc.transaction_svc.rollups_to_return = {"risks": {"pending_total": 0, "pending_high": 0}, "by_account": {}}


    out = await svc.get_dashboard(
        user_id=99,
        year=2025,
        month=11,
    )

    # check calls are made
    assert svc.account_svc.list_calls == [{"user_id": 99, "selected": True}]
    assert svc.budget_svc.calls == [{"user_id": 99, "year": 2025, "month": 11}]
    assert svc.transaction_svc.calls == [{"user_id": 99}]

    # no accounts
    assert out.totals == Decimal("0")
    assert out.accounts == []

    # budget should be all 0
    assert out.budget.budget == Decimal("0")
    assert out.budget.spent == Decimal("0")
    assert out.budget.available == Decimal("0")
    assert out.spending_categories == []


# TC-DASH-003: Category with 0 spent is skipped for graph data
@pytest.mark.anyio
async def test_get_dashboard_zero_spent_category(svc):
    svc.account_svc.accounts_to_return = [
        create_account(id=1, inst_name="Bank", current=50, available=50, name="Checking"),
    ]

    svc.budget_svc.budget_to_return = {
        "categories": [
            {
                "id": 1,
                "name": "Bills",
                "allotted_amount": Decimal("100.00"),
                "group": "Expenses",
                "spent_amount": "0.00",
                "remaining_amount": "100.00",
            },
            {
                "id": 2,
                "name": "Going Out",
                "allotted_amount": Decimal("200.00"),
                "group": "Expenses",
                "spent_amount": "50.00",
                "remaining_amount": "150.00",
            },
        ],
        "total_budgeted": "300.00",
        "total_spent": "50.00",
        "total_remaining": "250.00",
        "period": {"start_date": "2025-11-01", "end_date": "2025-12-01"},
    }

    svc.transaction_svc.rollups_to_return = {"risks": {"pending_total": 1, "pending_high": 1}, "by_account": {}}


    out: DashboardEntity = await svc.get_dashboard(
        user_id=1,
        year=2025,
        month=11,
    )

    assert len(out.spending_categories) == 1
    slice_ = out.spending_categories[0]

    assert slice_.name == "Going Out"
    assert slice_.amount == Decimal("50.00")
    assert slice_.percent == pytest.approx(100.0)


# TC-DASH-004: uses default date of today if not passed
@pytest.mark.anyio
async def test_get_dashboard_default_period(monkeypatch, svc):

    # mocking todays date
    class FakeDate(real_date):
        @classmethod
        def today(cls):
            # Pick something deterministic
            return cls(2025, 11, 15)

    # patching date
    monkeypatch.setattr("app.services.dashboard_service.date", FakeDate)


    # Mocking data
    svc.account_svc.accounts_to_return = [
        create_account(
            id=1,
            inst_name="Bank 1",
            current=Decimal("100.00"),
            available=Decimal("90.00"),
            name="Checking A",
        )
    ]

    svc.budget_svc.budget_to_return = {
        "categories": [],
        "total_budgeted": "0",
        "total_spent": "0",
        "total_remaining": "0",
        "period": {"start_date": "2025-11-01", "end_date": "2025-12-01"},
    }

    svc.transaction_svc.rollups_to_return = {"risks": {"pending_high": 0}, "by_account": {}}

    out = await svc.get_dashboard(user_id=7)


    assert len(svc.budget_svc.calls) == 1
    call = svc.budget_svc.calls[0]

    assert call["user_id"] == 7
    assert call["year"] == 2025
    assert call["month"] == 11

    # should be the mocked todays date
    assert out.period["year"] == 2025
    assert out.period["month"] == 11
    assert out.period["label"] == "November 2025"


    assert out.totals == Decimal("100.00")
    assert len(out.accounts) == 1
    assert out.accounts[0].institution_name == "Bank 1"