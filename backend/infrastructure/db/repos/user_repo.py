from typing import Optional, Sequence, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from app.db_interfaces import UserRepo
from app.domain.entities import UserEntity
from infrastructure.db.models.user import User

# returns data as domain entity to use in app 
def _to_entity(row: User) -> UserEntity:
    return UserEntity(id=row.id, email=row.email, name=row.name)

# this is an example to figure out the structure and workflow I want to follow
# create a class repository with all the capabilities app will need 
class SqlUserRepo(UserRepo):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, user_id: int) -> Optional[UserEntity]:
        res = await self.session.execute(select(User).where(User.id == user_id))
        row = res.scalar_one_or_none()
        return _to_entity(row) if row else None

    async def get_by_email(self, email: str) -> Optional[UserEntity]:
        res = await self.session.execute(select(User).where(User.email == email))
        row = res.scalar_one_or_none()
        return _to_entity(row) if row else None
    
    # creating this version that is private for auth use only so that typically the hashpassword isn't passed to services
    async def _get_by_email(self, email: str) -> Optional[User]:
        res = await self.session.execute(select(User).where(User.email == email))
        return res.scalar_one_or_none()

    async def list(self) -> Sequence[UserEntity]:
        res = await self.session.execute(select(User).order_by(User.id))
        return [_to_entity(r) for r in res.scalars().all()]

    async def add(self, user: UserEntity, password_hash) -> UserEntity:
        row = User(email=user.email, name=user.name, password_hash=password_hash)
        self.session.add(row)
        
        # pushes the id of the changes to the db so it'll create keys and defaults
        # dont have to flush if dont need data like id immediatly, 
        await self.session.flush()
        # pushes the final data and commits it and ends transaction
        await self.session.commit()
        # reloading the current state with the final db values after the commit
        # this does cost a SELECT so should only really do if the DB is going to update/set values that werent provided
        await self.session.refresh(row)
        return _to_entity(row)

    async def delete(self, user_id: int) -> None:
        await self.session.execute(delete(User).where(User.id == user_id))
        await self.session.commit()