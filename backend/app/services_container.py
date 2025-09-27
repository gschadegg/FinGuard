from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.plaid_service import PlaidService
from app.services.user_service import UserService
from infrastructure.db.repos.account_repo import SqlAccountRepo
from infrastructure.db.repos.connectionItem_repo import SqlConnectionItemRepo
from infrastructure.db.repos.user_repo import SqlUserRepo
from infrastructure.db.session import get_db


# want to be able to get a service that is then connected to the appropriate db repo and db session
async def get_user_service(db: AsyncSession = Depends(get_db)) -> UserService:
    repo = SqlUserRepo(db)
    return UserService(repo=repo)



async def get_plaid_service(db: AsyncSession = Depends(get_db)) -> PlaidService:
    account_repo = SqlAccountRepo(db)
    connection_item_repo = SqlConnectionItemRepo(db)
    return PlaidService(account_repo=account_repo, connection_item_repo=connection_item_repo)