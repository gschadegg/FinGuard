from datetime import date

from fastapi import HTTPException
from app.db_interfaces import AccountRepo, ConnectionItemRepo, TransactionRepo
from app.domain.entities import TransactionsPageEntity
from app.security.crypto import decrypt
from app.services.plaid_service import PlaidService


class TransactionService:
    def __init__(self, transaction_repo: TransactionRepo, 
                 account_repo: AccountRepo, connection_item_repo: ConnectionItemRepo, 
                 plaid: PlaidService):
        self.transaction_repo = transaction_repo
        self.account_repo = account_repo
        self.connection_item_repo = connection_item_repo
        self.plaid = plaid


    async def sync_connection_item(self, item_id: int, user_id: int) -> dict:
        item = await self.connection_item_repo.get_by_id(item_id)
        if not item or item.user_id != user_id:
            return {"ok": False, "reason": "Connection Item not found"}

        access_token = decrypt(item.access_token_encrypted)
        cursor = item.transactions_cursor

        added = modified = removed = 0
        while True:
            changed = await self.plaid.transactions_sync(access_token, cursor)
            for tx in changed["added"] + changed["modified"]:
                await self.transaction_repo.upsert_from_plaid(item, tx)
            if changed["removed"]:
                await self.transaction_repo.mark_removed([r["transaction_id"] 
                                                          for r in changed["removed"]])

            added += len(changed["added"]) 
            modified += len(changed["modified"]) 
            removed += len(changed["removed"])

            cursor = changed["next_cursor"]
            if not changed["has_more"]:
                break

        await self.connection_item_repo.update_transactions_cursor(item_id=item.id, cursor=cursor)
        return {"ok": True, "added": added, "modified": modified, "removed": removed}



    async def sync_user(self, user_id: int) -> dict:
        totals = {"ok": True, "added": 0, "modified": 0, "removed": 0}

        for item_id in await self.connection_item_repo.list_ids_by_user(user_id) or []:
            res = await self.sync_connection_item(item_id, user_id=user_id)
            if not res.get("ok"):
                continue

            totals["added"] += res["added"] 
            totals["modified"] += res["modified"] 
            totals["removed"] += res["removed"]

        return totals





    # pagination reading
    async def list_user(self, user_id: int, start: date | None, end: date | None, *,
                        selected_only: bool = True, 
                        limit: int = 50, cursor: str | None = None) -> TransactionsPageEntity:
        
        return await self.transaction_repo.list_by_user_paginated(
            user_id, 
            start, 
            end, 
            selected_only=selected_only, 
            limit=limit, 
            cursor=cursor
        )


    async def list_account(
            self, 
            account_id: int, 
            start: date | None, 
            end: date | None, 
            *,
            user_id: int,
            limit: int = 50, 
            cursor: str | None = None
        ) -> TransactionsPageEntity:

        account = await self.account_repo.get_one(account_id=account_id, plaid_account_id=None)
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")
        
        item = await self.connection_item_repo.get_by_id(account.item_id)
        if not item or item.user_id != user_id:
            raise HTTPException(status_code=404, detail="Account not found")
        
        return await self.transaction_repo.list_by_account_paginated(
            account_id, start, end, limit=limit, cursor=cursor)