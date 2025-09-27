from typing import Iterable, Union, Optional
from sqlalchemy import select, delete
from app.domain.entities import ConnectionItemEntity, AccountEntity
from infrastructure.db.models.connectionItem import ConnectionItem
from infrastructure.db.models.account import Account
from sqlalchemy.ext.asyncio import AsyncSession
from app.db_interfaces import ConnectionItemRepo

# returns data as domain entity to use in app 
def _to_entity(row: ConnectionItem) -> ConnectionItemEntity:
    return ConnectionItemEntity.model_validate(row, from_attributes=True)


def _account_rows_from_entities(parent: ConnectionItem, entities: Iterable["AccountEntity"]) -> list["Account"]:
    rows = []
    for e in entities:
        rows.append(Account( 
            item_id=parent.id,
            name=e.name,
            plaid_account_id=getattr(e, "plaid_account_id", None),
            mask=getattr(e, "mask", None),
            type=getattr(e, "type", None),
            subtype=getattr(e, "subtype", None),
            selected=True,
            item=parent
        ))
    return rows


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
                             access_token_encrypted=item.access_token_encrypted,
                             institution_id=item.institution_id,
                             institution_name=item.institution_name  
                            )
        self.session.add(row)
        await self.session.flush()

        if item.accounts:
            row.accounts.extend(_account_rows_from_entities(row, item.accounts))

        await self.session.refresh(row)
        await self.session.commit()
        return _to_entity(row)
    
    # update can be updated by finguard db id, plaid item id, or connection item obj
    async def update(
        self,
        item_or_entity: Union[int, str, ConnectionItemEntity], 
        token_encrypted: str,
        institution_id: Optional[str] = None,
        institution_name: Optional[str] = None,
    ) -> ConnectionItemEntity:
        
        # finguard db id: int
        if isinstance(item_or_entity, ConnectionItemEntity):
            row = await self.session.get(ConnectionItem, item_or_entity.id)
        # connection item obj
        elif isinstance(item_or_entity, int):
            row = await self.session.get(ConnectionItem, item_or_entity)
        # plaid item id: str
        elif isinstance(item_or_entity, str):
            res = await self.session.execute(
                select(ConnectionItem).where(ConnectionItem.plaid_item_id == item_or_entity)
            )
            row = res.scalars().first()
        else:
            row = None

        if row is None:
            raise ValueError("Connection not found")

        row.access_token_encrypted = token_encrypted
        if institution_id is not None:
            row.institution_id = institution_id
        if institution_name is not None:
            row.institution_name = institution_name

        await self.session.flush()
        await self.session.refresh(row)
        await self.session.commit()

        return ConnectionItemEntity.model_validate(row, from_attributes=True)