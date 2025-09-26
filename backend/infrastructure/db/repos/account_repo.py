from typing import Iterable
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, update
from app.domain.entities import AccountEntity
from infrastructure.db.models.account import Account
from app.db_interfaces import AccountRepo

# returns data as domain entity to use in app 
def _to_entity(row: Account) -> AccountEntity:
    return AccountEntity.model_validate(row)

class SqlAccountRepo(AccountRepo):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def upsert_selected(self, item_id: int, selected_accounts: Iterable[dict], unselect_others: bool = False) -> list[dict]:
        incoming_accounts = list(selected_accounts)
        plaid_ids = [a.plaid_account_id for a in incoming_accounts]

        result = await self.session.execute(
            select(Account)
            .where(Account.item_id == item_id, Account.plaid_account_id.in_(plaid_ids))
        )
        existing_accounts = result.scalars().all()
        by_plaid_id = {row.plaid_account_id: row for row in existing_accounts}

        touched_accounts: list[Account] = []
        for account in incoming_accounts:
            row = by_plaid_id.get(account.plaid_account_id)
            if row is None:
                row = Account(
                    item_id=item_id, 
                    plaid_account_id=account.plaid_account_id
                )
                self.session.add(row)
            row.name = account.name
            row.mask = account.mask
            row.type = account.type
            row.subtype = account.subtype
            row.selected = True
            touched_accounts.append(row)

        if unselect_others and plaid_ids:
            await self.session.execute(
                update(Account)
                .where(Account.item_id == item_id, Account.plaid_account_id.not_in(plaid_ids))
                .values(selected=False)
            )

        await self.session.flush()
        added_accounts = [{"id": r.id, "name": r.name, "plaid_account_id": r.plaid_account_id} for r in touched_accounts]
        await self.session.commit()
        return added_accounts