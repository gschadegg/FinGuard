from sqlalchemy import select, update, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date
from decimal import Decimal

from pydantic import BaseModel
from datetime import date as _date
from infrastructure.db.models import Transaction, Account, ConnectionItem
from app.domain.entities import TransactionEntity, ConnectionItemEntity
from app.utils.cursor import encode_cursor, decode_cursor
from sqlalchemy.dialects.postgresql import insert


PAGE_DEFAULT = 50
PAGE_MAX = 200

def _to_entity(row: Transaction) -> TransactionEntity:
    return TransactionEntity.model_validate(row, from_attributes=True)

class SqlTransactionRepo:
    def __init__(self, session: AsyncSession):
        self.session = session


    async def upsert_from_plaid(self, item: ConnectionItemEntity, plaid_data: dict) -> int:
        plaid_id = plaid_data["transaction_id"]
        pending_id = plaid_data.get("pending_transaction_id")
        account_plaid_id = plaid_data["account_id"]

        account_id = (await self.session.execute(
            select(Account.id).where(Account.plaid_account_id == account_plaid_id)
        )).scalar_one_or_none()

        # skipping if the account notin DB
        if account_id is None:
            return 0

        patch = _to_patch(plaid_data) 

        if pending_id:
            upd = (
                update(Transaction)
                .where(Transaction.pending_transaction_id == pending_id)
                .values(plaid_transaction_id=plaid_id, pending=False, **patch)
                .returning(Transaction.id)
            )
            merged_id = (await self.session.execute(upd)).scalar_one_or_none()
            if merged_id:
                return merged_id

        # inserting to db, using on conflict so only 1 pass
        ins = insert(Transaction).values(
            plaid_transaction_id=plaid_id,
            pending_transaction_id=pending_id,
            pending=plaid_data.get("pending", False),
            account_id=account_id,
            item_id=item.id,
            user_id=item.user_id,
            **patch,
        )

        upsert = ins.on_conflict_do_update(
            index_elements=[Transaction.plaid_transaction_id],
            set_=patch,  # trying to limit updated to only plaid related fields
        ).returning(Transaction.id)

        return (await self.session.execute(upsert)).scalar_one()



    async def mark_removed(self, plaid_ids: list[str]) -> None:
        if not plaid_ids:
            return
        await self.session.execute(
            update(Transaction).where(Transaction.plaid_transaction_id.in_(plaid_ids)).values(removed=True)
        )
        await self.session.flush()



    async def list_by_user_paginated(
        self, user_id: int, start_date: date | None, end_date: date | None,
        *, selected_only: bool = True, limit: int, cursor: str | None
    ) -> dict:
        limit = max(1, min(limit or PAGE_DEFAULT, PAGE_MAX))

        transactions = select(Transaction).where(
            Transaction.user_id == user_id,
            Transaction.removed.is_(False),
        )
        if start_date:
            transactions = transactions.where(Transaction.date >= start_date)
        if end_date:
            transactions = transactions.where(Transaction.date <= end_date)

        if selected_only:
            transactions = transactions.join(Account, Account.id == Transaction.account_id).where(Account.selected.is_(True))

        transactions = transactions.order_by(Transaction.date.desc(), Transaction.id.desc())

        if cursor:
            cursor_date, cursor_id = decode_cursor(cursor)
            transactions = transactions.where(
                or_(
                    Transaction.date < cursor_date,
                    and_(Transaction.date == cursor_date, Transaction.id < cursor_id),
                )
            )

        transactions = transactions.limit(limit + 1)
        rows = (await self.session.execute(transactions)).scalars().all()
        has_more = len(rows) > limit
        items = rows[:limit]
        next_cursor = encode_cursor(items[-1].date, items[-1].id) if has_more else None

        return {"items": [_to_entity(r) for r in items], "next_cursor": next_cursor, "has_more": has_more}



    async def list_by_account_paginated(
        self, account_id: int, start_date: date | None, end_date: date | None,
        *, limit: int, cursor: str | None
    ) -> dict:
        limit = max(1, min(limit or PAGE_DEFAULT, PAGE_MAX))

        transactions = select(Transaction).where(
            Transaction.account_id == account_id,
            Transaction.removed.is_(False),
        )
        if start_date:
            transactions = transactions.where(Transaction.date >= start_date)
        if end_date:
            transactions = transactions.where(Transaction.date <= end_date)

        transactions = transactions.order_by(Transaction.date.desc(), Transaction.id.desc())

        if cursor:
            cursor_date, cursor_id = decode_cursor(cursor)
            transactions = transactions.where(
                or_(
                    Transaction.date < cursor_date,
                    and_(Transaction.date == cursor_date, Transaction.id < cursor_id),
                )
            )

        transactions = transactions.limit(limit + 1)
        rows = (await self.session.execute(transactions)).scalars().all()
        has_more = len(rows) > limit
        items = rows[:limit]
        next_cursor = encode_cursor(items[-1].date, items[-1].id) if has_more else None

        return {"items": [_to_entity(r) for r in items], "next_cursor": next_cursor, "has_more": has_more}





# needed for converting plaid dictionarys recieved to patch into db rows
class _TransactionPatch(BaseModel):
    name: str | None = None
    merchant_name: str | None = None
    amount: Decimal | float | None = None
    iso_currency_code: str | None = None
    date: _date| None = None
    authorized_date: _date| None = None
    category: str | None = None
    category_id: str | None = None
    payment_channel: str | None = None

def _to_patch(p: dict) -> dict:
    iso = p.get("iso_currency_code") or (p.get("balances") or {}).get("iso_currency_code")
    cats = p.get("category") or []
    model = _TransactionPatch(
        name=p.get("name"),
        merchant_name=p.get("merchant_name"),
        amount=p.get("amount"),
        iso_currency_code=iso,
        date=p.get("date"),
        authorized_date=p.get("authorized_date"),
        category=(" > ".join(cats) if cats else None),
        category_id=p.get("category_id"),
        payment_channel=p.get("payment_channel"),
    )
    return model.model_dump(exclude_none=True)

def _apply_patch(t: Transaction, p: dict) -> None:
    patch = _to_patch(p)
    for k, v in patch.items():
        setattr(t, k, v)