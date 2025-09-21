from typing import Iterable
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from app.domain.entities import AccountEntity
from infrastructure.db.models.account import Account
from app.db_interfaces import AccountRepo

# returns data as domain entity to use in app 
def _to_entity(row: Account) -> AccountEntity:
    return AccountEntity(id=row.id, email=row.email, name=row.name)

class SqlAccountRepo(AccountRepo):
    def __init__(self, session: AsyncSession):
        self.session = session

    def upsert_selected(self, item_id: int, selectedAccount: Iterable[dict]) -> None:
        for a in selectedAccount:
            acc = self.session.exec(select(Account).where(Account.plaid_account_id == a["id"])).first()
            if not acc:
                acc = Account(item_id=item_id, plaid_account_id=a["id"])
                self.session.add(acc)
            acc.name = a.get("name"); acc.mask = a.get("mask"); acc.selected = True
        self.session.commit()