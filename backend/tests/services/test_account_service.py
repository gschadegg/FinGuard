import pytest
from types import SimpleNamespace
from typing import List, Optional, Dict

from app.services.account_service import AccountService
from app.domain.entities import ConnectionItemEntity, AccountEntity, FullAccountEntity
from app.domain.errors import NotFoundError

class MockAccountRepo:
    def __init__(self):
        self._list_rows: List[SimpleNamespace] = []
        self._one: Optional[SimpleNamespace] = None
        self.list_calls: List[dict] = []
        self.get_one_calls: List[dict] = []

    async def list_by_user_id(self, user_id, selected):
        self.list_calls.append({"user_id": user_id, "selected": selected})
        return self._list_rows

    async def get_one(self, *, account_id=None, plaid_account_id=None):
        self.get_one_calls.append({"account_id": account_id, "plaid_account_id": plaid_account_id})
        return self._one


class MockConnectionItemRepo:
    def __init__(self):
        self.single_item: Optional[ConnectionItemEntity] = None
        
        self.get_by_id_calls = 0

    async def get_by_id(self, id: int) -> Optional[ConnectionItemEntity]:
        self.get_by_id_calls += 1
        return self.single_item


class MockPlaidService:
    def __init__(self):
        self.calls: List[dict] = []
        self.preloads: Dict[tuple, Dict[str, dict]] = {}

    async def get_accounts(self, *, access_token: Optional[str] = None, item_id: Optional[int] = None, account_ids: Optional[List[str]] = None) -> Dict[str, dict]:
        self.calls.append({"item_id": item_id, "account_ids": list(account_ids or [])})
        key = (item_id, tuple(sorted(account_ids or [])))
        if key in self.preloads:
            return self.preloads[key]
        return {aid: {"account_id": aid, "name": f"name-{aid}"} for aid in (account_ids or [])}



def map_to_account_entity(
    id: int,
    item_id: int,
    plaid_id: str,
    name: str = "name",
    mask: str = "mask",
    type_: str = "type",
    subtype: str = "subtype",
    selected: bool = True,
    inst_id: str | None = None,
    inst_name: str | None = None,
) -> AccountEntity:
    return AccountEntity(
        id=id,
        item_id=item_id,
        plaid_account_id=plaid_id,
        name=name,
        mask=mask,
        type=type_,      
        subtype=subtype,
        selected=selected,
        institution_id=inst_id,
        institution_name=inst_name,
    )


############################
# list_all_user_accounts Tests
############################

# TC-ACCT-LIST-001: BASE scenario returns accounts with Plaid details
@pytest.mark.anyio
async def test_list_all_user_accounts_base(monkeypatch):
    repo = MockAccountRepo()
    repo._list_rows = [
        map_to_account_entity(1, item_id=42, plaid_id="account1", name="A"),
        map_to_account_entity(2, item_id=42, plaid_id="account2", name="B"),
    ]


    connection = MockConnectionItemRepo()
    connection.single_item = ConnectionItemEntity(
        id=42, user_id=99, plaid_item_id="item-42",
        access_token_encrypted="X", institution_id="institution3", institution_name="Chase", accounts=[]
    )
    plaid = MockPlaidService()

    svc = AccountService(account_repo=repo, connection_item_repo=connection, plaid=plaid)

    out = await svc.list_all_user_accounts(user_id=7, selected=True)

    assert len(out) == 2
    assert out[0].plaid is not None and out[1].plaid is not None

    assert len(plaid.calls) == 1
    call = plaid.calls[0]
    assert call["item_id"] == 42
    assert set(call["account_ids"]) == {"account1", "account2"}


    assert connection.get_by_id_calls == 1

    assert out[0].institution_id == "institution3"
    assert out[0].institution_name == "Chase"


# TC-ACCT-LIST-002: No accounts found
@pytest.mark.anyio
async def test_list_all_user_accounts_none(monkeypatch):
    repo = MockAccountRepo()
    repo._list_rows = []
    connection = MockConnectionItemRepo()
    plaid = MockPlaidService()
    svc = AccountService(account_repo=repo, connection_item_repo=connection, plaid=plaid)

    with pytest.raises(NotFoundError):
        await svc.list_all_user_accounts(user_id=1, selected=True)



# TC-ACCT-LIST-003: Plaid returns empty when getting details
@pytest.mark.anyio
async def test_list_all_user_accounts_plaid_empty(monkeypatch):
    repo = MockAccountRepo()
    repo._list_rows = [map_to_account_entity(1, item_id=42, plaid_id="account1", name="A")]
    connection = MockConnectionItemRepo()
    connection.single_item = ConnectionItemEntity(
        id=42, user_id=99, plaid_item_id="item-42",
        access_token_encrypted="X", institution_id="institution3", institution_name="Chase", accounts=[]
    )
    plaid = MockPlaidService()

    plaid.preloads[(42, tuple(["account1"]))] = {}

    svc = AccountService(account_repo=repo, connection_item_repo=connection, plaid=plaid)

    out = await svc.list_all_user_accounts(user_id=7, selected=True)

    assert len(out) == 1
    assert out[0].plaid is None
    assert out[0].name == "A" 



# TC-ACCT-LIST-004: Plaid is called for each item
@pytest.mark.anyio
async def test_list_all_user_accounts_grouping_two_items(monkeypatch):
    repo = MockAccountRepo()
    repo._list_rows = [
        map_to_account_entity(1, item_id=1, plaid_id="A1"), map_to_account_entity(2, item_id=1, plaid_id="A2"),
        map_to_account_entity(3, item_id=2, plaid_id="B1")
    ]
    connection = MockConnectionItemRepo()
    connection.single_item = ConnectionItemEntity(
        id=1, user_id=99, plaid_item_id="item-1",
        access_token_encrypted="encrypted-token", institution_id="institution3", institution_name="Bank Name", accounts=[]
    )
    plaid = MockPlaidService()

    svc = AccountService(account_repo=repo, connection_item_repo=connection, plaid=plaid)
    out = await svc.list_all_user_accounts(user_id=7, selected=True)

    assert len(out) == 3
    assert len(plaid.calls) == 2

    calls = [{ "item_id": c["item_id"], "ids": set(c["account_ids"]) } for c in plaid.calls]
    assert { (c["item_id"], tuple(sorted(c["ids"]))) for c in calls } == {
        (1, tuple(sorted({"A1","A2"}))),
        (2, tuple(sorted({"B1"}))),
    }


############################
# get_account_by_id Tests
############################

# TC-ACCT-GET-001: BASE scenario, get account by id
@pytest.mark.anyio
async def test_get_account_by_id_base(monkeypatch):

    repo = MockAccountRepo()
    repo._one = map_to_account_entity(10, item_id=77, plaid_id="p-1", name="DBName")
    connection = MockConnectionItemRepo()
    connection.single_item = ConnectionItemEntity(
        id=77, user_id=99, plaid_item_id="item-77",
        access_token_encrypted="encrypted-token", institution_id="institution3", institution_name="My Bank", accounts=[]
    )

    plaid = MockPlaidService()
    plaid.preloads[(77, tuple(["p-1"]))] = {"p-1": {"account_id": "p-1", "name": "PlaidName"}}

    svc = AccountService(account_repo=repo, connection_item_repo=connection, plaid=plaid)
    out = await svc.get_account_by_id(account_id=10, plaid_account_id=None)

    assert out.id == 10
    assert out.name == "DBName"
    assert out.plaid is not None
    assert out.plaid.account_id == "p-1"
    assert out.institution_name == "My Bank"

    assert len(plaid.calls) == 1
    assert plaid.calls[0]["item_id"] == 77
    assert plaid.calls[0]["account_ids"] == ["p-1"]


# TC-ACCT-GET-002: Account not found
@pytest.mark.anyio
async def test_get_account_by_id_not_found(monkeypatch):
    repo = MockAccountRepo()
    repo._one = None
    connection = MockConnectionItemRepo()
    plaid = MockPlaidService()

    svc = AccountService(account_repo=repo, connection_item_repo=connection, plaid=plaid)
    with pytest.raises(NotFoundError):
        await svc.get_account_by_id(account_id=123, plaid_account_id=None)

