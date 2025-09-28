import pytest
from types import SimpleNamespace
from typing import Optional, List
from datetime import date

from app.services.transaction_service import TransactionService
from app.domain.entities import ConnectionItemEntity 


class MockTransactionRepo:
    def __init__(self):
        self.upsert_calls: list[tuple[ConnectionItemEntity, dict]] = []
        self.removed_ids: list[str] = []


        self.page_user = {"items": [], "next_cursor": None, "has_more": False}
        self.page_account = {"items": [], "next_cursor": None, "has_more": False}


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


class MockAccountRepo:
    pass


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
    plaid = MockPlaidService()

    svc = TransactionService(transaction_repo=transaction_repo, account_repo=account_repo,
                             connection_item_repo=connection_item_repo, plaid=plaid)


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

    out = await svc.sync_connection_item(42)

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

    out = await svc.sync_connection_item(99)

    assert out == {"ok": True, "added": 1, "modified": 2, "removed": 0}
    assert len(svc.transaction_repo.upsert_calls) == 3

    assert svc.plaid.calls == [("decrypted-access-token", None), ("decrypted-access-token", "c1")]
    assert svc.connection_item_repo.update_cursor_calls == [(99, "c2")]


# TC-TX-ITEM-003: connection item not found
@pytest.mark.anyio
async def test_sync_connection_item_item_not_found(svc):
    # no entry in _by_id
    out = await svc.sync_connection_item(555)

    assert out == {"ok": False, "reason": "Connection Item not found"}
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

    async def _mock_sync_connection_item(item_id: int):
        if item_id == 1:
            return {"ok": True, "added": 2, "modified": 1, "removed": 0}
        if item_id == 2:
            return {"ok": False, "reason": "boom"}
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
    out = await svc.list_account(account_id=123, start=None, end=date(2025, 12, 31),
                                 limit=25, cursor=None)

    assert out == {"items": [{"id": 11}], "next_cursor": None, "has_more": False}
    assert svc.transaction_repo.page_account["_last_args"] == {
        "account_id": 123, "start": None, "end": date(2025, 12, 31),
        "limit": 25, "cursor": None,
    }