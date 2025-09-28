from typing import Iterable, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, update
from app.domain.entities import AccountEntity
from infrastructure.db.models.account import Account
from infrastructure.db.models.connectionItem import ConnectionItem
from app.db_interfaces import AccountRepo
from fastapi import HTTPException, status

from sqlalchemy.orm import joinedload


# returns data as domain entity to use in app 
def _to_entity(row: Account) -> AccountEntity:
    return AccountEntity.model_validate(row)

class SqlAccountRepo(AccountRepo):
    def __init__(self, session: AsyncSession):
        self.session = session


    async def list_by_user_id(
        self,
        user_id: int,
        only_selected: Optional[bool] = True,
    ) -> list[AccountEntity]:

        found_accounts = (
            select(Account)
            .join(ConnectionItem, Account.item_id == ConnectionItem.id)
            .where(ConnectionItem.user_id == user_id)
            .options(joinedload(Account.item))
        )


        if only_selected is True:
            found_accounts = found_accounts.where(Account.selected.is_(True))
        elif only_selected is False:
            found_accounts = found_accounts.where(Account.selected.is_(False))


        rows = (await self.session.execute(found_accounts)).scalars().all()
        return [_to_entity(r) for r in rows]


    async def get_one(
        self,
        *,
        account_id: Optional[int] = None,
        plaid_account_id: Optional[str] = None,
    ) -> Optional[AccountEntity]:

        if (account_id is None) == (plaid_account_id is None):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Requires an account ID",
            )

        if account_id is not None:
            found_account = select(Account).where(Account.id == account_id)
        else:
            found_account = select(Account).where(Account.plaid_account_id == plaid_account_id)

        row = (await self.session.execute(found_account)).scalars().first()
        return _to_entity(row) if row else None
    



    async def upsert_selected(
            self, 
            item_id: int, 
            selected_accounts: Iterable[dict], 
            unselect_others: bool = False,
            institution_id: str | None = None,
            institution_name: str | None = None
        ) -> list[dict]:
        
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
            row.institution_id = account.institution_id
            row.institution_name = account.institution_name

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