import pytest
from types import SimpleNamespace
from typing import Optional, List
from datetime import date
from fastapi import HTTPException

from app.services.transaction_service import TransactionService
from app.domain.entities import ConnectionItemEntity, AccountEntity, BudgetCategoryEntity


class MockTransactionRepo:
    def __init__(self):
        self.upsert_calls: list[tuple[ConnectionItemEntity, dict]] = []
        self.removed_ids: list[str] = []


        self.page_user = {"items": [], "next_cursor": None, "has_more": False}
        self.page_account = {"items": [], "next_cursor": None, "has_more": False}

        self._tx_by_id: dict[int, dict] = {}
        self.set_category_calls: list[tuple[int, int | None]] = [] 

    def _createTransaction(self, *, txn_id: int, user_id: int, category_id: int | None):
        self._tx_by_id[txn_id] = {"id": txn_id, "user_id": user_id, "category_id": category_id}

    async def upsert_from_plaid(self, item: ConnectionItemEntity, transaction: dict) -> int:
        self.upsert_calls.append((item, transaction))
        return 1

    async def mark_removed(self, plaid_ids: list[str]) -> None:
        self.removed_ids.extend(plaid_ids)


    async def list_by_user_paginated(
            self, 
            user_id: int, 
            start: Optional[date], 
            end: Optional[date], 
            *,
            selected_only: bool, 
            limit: int, 
            cursor: Optional[str]
        ) -> dict:

        self.page_user["_last_args"] = dict(
            user_id=user_id, 
            start=start, 
            end=end,
            selected_only=selected_only, 
            limit=limit, 
            cursor=cursor
        )

        return {key: val for key, val in self.page_user.items() if key != "_last_args"}

    async def list_by_account_paginated(
            self,
            account_id: int, 
            start: Optional[date], 
            end: Optional[date], 
            *,
            limit: int, 
            cursor: Optional[str]
        ) -> dict:

        self.page_account["_last_args"] = dict(
            account_id=account_id, 
            start=start, 
            end=end,
            limit=limit, 
            cursor=cursor
        )
        return {key: val for key, val in self.page_account.items() if key != "_last_args"}
    


    async def get_owned(self, user_id: int, transaction_id: int):
        tx = self._tx_by_id.get(transaction_id)

        if tx and tx["user_id"] == user_id:
            return tx
        
        return None


    async def set_transaction_category(self, user_id: int, transaction_id: int, category_id: int | None) -> bool:
        tx = self._tx_by_id.get(transaction_id)

        if not tx or tx["user_id"] != user_id:
            return False
        
        tx["category_id"] = category_id
        self.set_category_calls.append((transaction_id, category_id))

        return True


class MockAccountRepo:
    def __init__(self):
        self._by_id: dict[int, AccountEntity] = {}

    async def get_one(self, *, account_id=None, plaid_account_id=None):
        if account_id is not None:
            return self._by_id.get(account_id)
        if plaid_account_id is not None:
            for account in self._by_id.values():
                if account.plaid_account_id == plaid_account_id:
                    return account
        return None


class MockConnectionItemRepo:
    def __init__(self):
        self._by_id: dict[int, ConnectionItemEntity] = {}
        self.list_ids: list[int] = []
        self.update_cursor_calls: list[tuple[int, Optional[str]]] = []

    async def get_by_id(self, id: int) -> Optional[ConnectionItemEntity]:
        return self._by_id.get(id)

    async def list_ids_by_user(self, user_id: int) -> list[int]:
        return list(self.list_ids)

    async def update_transactions_cursor(self, item_id: int, cursor: Optional[str]) -> None:
        self.update_cursor_calls.append((item_id, cursor))


class MockBudgetCategoryRepo:
    def __init__(self):
        self._by_id: dict[int, BudgetCategoryEntity] = {}
        self._owned: dict[int, dict] = {}

    def _createCategory(self, *, category_id: int, user_id: int):
        self._owned[category_id] = {"id": category_id, "user_id": user_id}

    async def get_owned(self, user_id: int, category_id: int):
        category = self._owned.get(category_id)

        if category and category["user_id"] == user_id:
            return category
        
        return None


class MockPlaidService:
    def __init__(self):
        self.calls: list[tuple[str, Optional[str]]] = []   #this will be the  (access_token, cursor) passed
        self.queue: list[dict] = []   

    async def transactions_sync(self, access_token: str, cursor: Optional[str]) -> dict:
        self.calls.append((access_token, cursor))
        if self.queue:
            return self.queue.pop(0)
        return {"added": [], "modified": [], "removed": [], "next_cursor": cursor, "has_more": False}



@pytest.fixture
def svc(monkeypatch):
    monkeypatch.setattr("app.services.transaction_service.decrypt", lambda s: "decrypted-access-token")

    transaction_repo = MockTransactionRepo()
    account_repo = MockAccountRepo()
    connection_item_repo = MockConnectionItemRepo()
    budget_category_repo = MockBudgetCategoryRepo()
    plaid = MockPlaidService()

    svc = TransactionService(transaction_repo=transaction_repo, account_repo=account_repo,
                             connection_item_repo=connection_item_repo, plaid=plaid, budget_category_repo=budget_category_repo)


    svc.transaction_repo = transaction_repo
    svc.connection_item_repo = connection_item_repo
    svc.plaid = plaid
    return svc


def _item(item_id=42, user_id=7, cursor=None) -> ConnectionItemEntity:
    return ConnectionItemEntity(
        id=item_id,
        user_id=user_id,
        plaid_item_id="plaid-item-123",
        access_token_encrypted="encrypted",
        transactions_cursor=cursor,
        accounts=[],
        institution_id=None,
        institution_name=None,
    )



############################
# sync_connection_item Tests
############################

# TC-TX-ITEM-001: Base scenario sync returns upserts added and modified 
@pytest.mark.anyio
async def test_sync_connection_item_base(svc):
    svc.connection_item_repo._by_id[42] = _item(item_id=42, user_id=7, cursor=None)

    svc.plaid.queue = [
        {
            "added":    [{"transaction_id": "a1", "account_id": "account1"}, {"transaction_id": "a2", "account_id": "account1"}],
            "modified": [{"transaction_id": "m1", "account_id": "account2"}],
            "removed":  [{"transaction_id": "r1"}],
            "next_cursor": "cursor-1",
            "has_more": False,
        }
    ]

    out = await svc.sync_connection_item(42, user_id=7)

    assert out == {"ok": True, "added": 2, "modified": 1, "removed": 1}
    assert len(svc.transaction_repo.upsert_calls) == 3

    assert svc.transaction_repo.removed_ids == ["r1"]
    assert svc.connection_item_repo.update_cursor_calls == [(42, "cursor-1")]


    assert svc.plaid.calls == [("decrypted-access-token", None)]


# TC-TX-ITEM-002: multiple page, keep syncing until it hits has_more == false 
@pytest.mark.anyio
async def test_sync_connection_item_multi_page(svc):
    svc.connection_item_repo._by_id[99] = _item(item_id=99, user_id=1, cursor=None)

    svc.plaid.queue = [
        {"added": [{"transaction_id": "t1", "account_id": "p1"}], "modified": [], "removed": [], "next_cursor": "c1", "has_more": True},
        {"added": [], 
         "modified": [{"transaction_id": "t2", "account_id": "p2"}, {"transaction_id": "t3", "account_id": "p2"}], "removed": [], "next_cursor": "c2", "has_more": False},
    ]

    out = await svc.sync_connection_item(99, user_id=1)

    assert out == {"ok": True, "added": 1, "modified": 2, "removed": 0}
    assert len(svc.transaction_repo.upsert_calls) == 3

    assert svc.plaid.calls == [("decrypted-access-token", None), ("decrypted-access-token", "c1")]
    assert svc.connection_item_repo.update_cursor_calls == [(99, "c2")]


# TC-TX-ITEM-003: connection item not found
@pytest.mark.anyio
async def test_sync_connection_item_item_not_found(svc):
    resp = await svc.sync_connection_item(555, user_id=7)

    assert resp == {"ok": False, "reason": "Connection Item not found"}
    assert svc.plaid.calls == []
    assert svc.transaction_repo.upsert_calls == []
    assert svc.transaction_repo.removed_ids == []
    assert svc.connection_item_repo.update_cursor_calls == []


#TC-TX-ITEM-004: connection item found but not owned by current user
@pytest.mark.anyio
async def test_sync_connection_item_not_owned(svc):
    # mock connection item with user_id 999
    svc.connection_item_repo._by_id[77] = _item(item_id=77, user_id=999, cursor=None)

    #requesting connection item and its sync with user_id 1
    resp = await svc.sync_connection_item(77, user_id=1)

    assert resp == {"ok": False, "reason": "Connection Item not found"}

    # Shouldnt touch plaid or db
    assert svc.plaid.calls == []
    assert svc.transaction_repo.upsert_calls == []
    assert svc.transaction_repo.removed_ids == []
    assert svc.connection_item_repo.update_cursor_calls == []



############################
# sync_user Tests
############################


# TC-TX-USER-001: base scenario,  syncs all connections owned by user
@pytest.mark.anyio
async def test_sync_user_base(monkeypatch, svc):
    svc.connection_item_repo.list_ids = [1, 2, 3]

    async def _mock_sync_connection_item(item_id: int, **kwargs):
        if item_id == 1:
            return {"ok": True, "added": 2, "modified": 1, "removed": 0}
        if item_id == 2:
            return {"ok": False, "reason": "error"}
        return {"ok": True, "added": 0, "modified": 3, "removed": 1}

    monkeypatch.setattr(svc, "sync_connection_item", _mock_sync_connection_item)

    out = await svc.sync_user(user_id=7)

    assert out == {"ok": True, "added": 2, "modified": 4, "removed": 1}

# TC-TX-USER-002: no connections found for user
@pytest.mark.anyio
async def test_sync_user_no_items(monkeypatch, svc):
    svc.connection_item_repo.list_ids = []

    calls = []
    async def _spy_sync_connection_item(item_id: int):
        calls.append(item_id)
        return {"ok": True, "added": 1, "modified": 1, "removed": 1}

    monkeypatch.setattr(svc, "sync_connection_item", _spy_sync_connection_item)

    sync_data = await svc.sync_user(user_id=7)

    assert sync_data == {"ok": True, "added": 0, "modified": 0, "removed": 0}
    assert calls == [] 




############################
# list_user & list_account Tests
############################


# TC-TX-LIST-001: returns a page of transactions fetched by user
@pytest.mark.anyio
async def test_list_user_get(svc):
    svc.transaction_repo.page_user = {
        "items": [{"id": 1}], "next_cursor": "nc", "has_more": True
    }
    out = await svc.list_user(user_id=9, start=date(2025, 1, 1), end=None,
                              selected_only=False, limit=5, cursor="cur-x")

    assert out == {"items": [{"id": 1}], "next_cursor": "nc", "has_more": True}
    assert svc.transaction_repo.page_user["_last_args"] == {
        "user_id": 9, "start": date(2025, 1, 1), "end": None,
        "selected_only": False, "limit": 5, "cursor": "cur-x",
    }


# TC-TX-LIST-002: returns a page of transactions fetched by account
@pytest.mark.anyio
async def test_list_account_get(svc):
    svc.transaction_repo.page_account = {
        "items": [{"id": 11}], "next_cursor": None, "has_more": False
    }

    svc.account_repo._by_id[123] = AccountEntity(
        id=123, item_id=55, plaid_account_id="plaid-account-1",
        name=None, mask=None, type=None, subtype=None, selected=True,
        institution_id=None, institution_name=None
    )
    svc.connection_item_repo._by_id[55] = _item(item_id=55, user_id=1, cursor=None)

    out = await svc.list_account(account_id=123, start=None, end=date(2025, 12, 31),
                                 limit=25, cursor=None, user_id=1)

    assert out == {"items": [{"id": 11}], "next_cursor": None, "has_more": False}
    assert svc.transaction_repo.page_account["_last_args"] == {
        "account_id": 123, "start": None, "end": date(2025, 12, 31),
        "limit": 25, "cursor": None,
    }


#TC-TX-LIST-003: account is found but not owned by current user
@pytest.mark.anyio
async def test_list_account_not_owned(svc):
    svc.account_repo._by_id[123] = AccountEntity(
        id=123, item_id=55, plaid_account_id="plaid-account-1",
        name=None, mask=None, type=None, subtype=None, selected=True,
        institution_id=None, institution_name=None
    )
    #mock connection item with user_id 999
    svc.connection_item_repo._by_id[55] = _item(item_id=55, user_id=999, cursor=None)

    # request account on connection item with user_id 1
    with pytest.raises(HTTPException) as ei:
        await svc.list_account(account_id=123, start=None, end=None, limit=50, cursor=None, user_id=1)

    assert ei.value.status_code == 404
    # pagination shouldnt have been call
    assert "_last_args" not in svc.transaction_repo.page_account





############################
# assign_category Tests
############################

# TC-TX-CAT-001: base scenario, assign an owned transaction to an owned category
@pytest.mark.anyio
async def test_assign_category_base(svc):
    svc.transaction_repo._createTransaction(txn_id=101, user_id=7, category_id=None)
    svc.budget_category_repo._createCategory(category_id=55, user_id=7)

    out = await svc.assign_category(user_id=7, transaction_id=101, category_id=55)

    assert out == {"ok": True}

    assert svc.transaction_repo._tx_by_id[101]["category_id"] == 55
    assert svc.transaction_repo.set_category_calls == [(101, 55)]


# TC-TX-CAT-002: set category to unassigned
@pytest.mark.anyio
async def test_assign_category_unassigned(svc):
    svc.transaction_repo._createTransaction(txn_id=202, user_id=7, category_id=10)

    out = await svc.assign_category(user_id=7, transaction_id=202, category_id=None)

    assert out == {"ok": True}
    assert svc.transaction_repo._tx_by_id[202]["category_id"] is None
    assert svc.transaction_repo.set_category_calls[-1] == (202, None)


# TC-TX-CAT-003: transaction not found
@pytest.mark.anyio
async def test_assign_category_txn_not_found(svc):
    with pytest.raises(HTTPException) as exception:
        await svc.assign_category(user_id=7, transaction_id=999, category_id=55)

    assert exception.value.status_code == 404
    assert "Transaction not found" in exception.value.detail

    # shouldnt have called the set category function
    assert svc.transaction_repo.set_category_calls == []



# TC-TX-CAT-004: category isn't owned by user
@pytest.mark.anyio
async def test_assign_category_category_not_owned(svc):
    svc.transaction_repo._createTransaction(txn_id=303, user_id=7, category_id=None)

    svc.budget_category_repo._createCategory(category_id=77, user_id=8)

    with pytest.raises(HTTPException) as exception:
        await svc.assign_category(user_id=7, transaction_id=303, category_id=77)

    assert exception.value.status_code == 404
    assert "Category not found" in exception.value.detail

    # shouldnt have called the set category function
    assert svc.transaction_repo.set_category_calls == []



# TC-TX-CAT-005: change category assigned to different category
@pytest.mark.anyio
async def test_assign_category_reassign(svc):
    svc.transaction_repo._createTransaction(txn_id=404, user_id=7, category_id=11)
    svc.budget_category_repo._createCategory(category_id=11, user_id=7)
    svc.budget_category_repo._createCategory(category_id=12, user_id=7)

    out1 = await svc.assign_category(user_id=7, transaction_id=404, category_id=12)

    out2 = await svc.assign_category(user_id=7, transaction_id=404, category_id=None)
    out3 = await svc.assign_category(user_id=7, transaction_id=404, category_id=11)

    assert out1 == {"ok": True} and out2 == {"ok": True} and out3 == {"ok": True}
    assert svc.transaction_repo._tx_by_id[404]["category_id"] == 11
