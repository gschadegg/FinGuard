from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from infrastructure.db.session import get_db 
from infrastructure.db.repos.user_repo import SqlAlchemyUserRepo
from app.services.user_service import UserService

# want to be able to get a service that is then connected to the appropriate db repo and db session
async def get_user_service(db: AsyncSession = Depends(get_db)) -> UserService:
    repo = SqlAlchemyUserRepo(db)
    return UserService(repo=repo)