from typing import Iterable
from sqlalchemy import select, delete
from app.domain.entities import ConnectionItemEntity
from infrastructure.db.models.connectionItem import ConnectionItem
from sqlalchemy.ext.asyncio import AsyncSession
from app.db_interfaces import ConnectionItemRepo

# returns data as domain entity to use in app 
def _to_entity(row: ConnectionItem) -> ConnectionItemEntity:
    return ConnectionItemEntity(id=row.id, 
                                user_id=row.user_id, 
                                plaid_item_id=row.plaid_item_id, 
                                created_at=row.created_at, 
                                accounts=row.accounts,
                                access_token_encrypted=row.access_token_encrypted )


class SqlConnectionItemRepo(ConnectionItemRepo):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_connection_item_id(self, plaid_item_id: str):
        result = await self.session.execute(
            select(ConnectionItem).where(ConnectionItem.plaid_item_id == plaid_item_id)
        )
        item = result.scalar_one_or_none()
        return _to_entity(item) if item else None

    async def add(self, item: ConnectionItemEntity) -> ConnectionItemEntity:
        row = ConnectionItem(id=item.id, 
                             user_id=item.user_id, 
                             plaid_item_id=item.plaid_item_id, 
                             created_at=item.created_at, 
                             accounts=item.accounts,
                             access_token_encrypted=item.access_token_encrypted )
        self.session.add(row)
        await self.session.flush()
        await self.session.refresh(row)
        await self.session.commit()
        return _to_entity(row)