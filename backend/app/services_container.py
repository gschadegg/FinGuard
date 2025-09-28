from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.account_service import AccountService
from app.services.plaid_service import PlaidService
from app.services.transaction_service import TransactionService
from app.services.user_service import UserService
from infrastructure.db.repos.account_repo import SqlAccountRepo
from infrastructure.db.repos.connectionItem_repo import SqlConnectionItemRepo
from infrastructure.db.repos.transaction_repo import SqlTransactionRepo
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


async def get_account_service(
        db: AsyncSession = Depends(get_db), 
        plaid: PlaidService = Depends(get_plaid_service)
    ) -> AccountService:
    
    account_repo = SqlAccountRepo(db)
    connection_item_repo = SqlConnectionItemRepo(db)

    return AccountService(
        account_repo=account_repo, 
        connection_item_repo=connection_item_repo, 
        plaid=plaid
    )


async def get_transaction_service(
        db: AsyncSession = Depends(get_db), 
        plaid: PlaidService = Depends(get_plaid_service)
    ) -> TransactionService:
    
    account_repo = SqlAccountRepo(db)
    connection_item_repo = SqlConnectionItemRepo(db)
    transaction_repo = SqlTransactionRepo(db)

    return TransactionService(
        account_repo=account_repo, 
        connection_item_repo=connection_item_repo, 
        transaction_repo=transaction_repo,
        plaid=plaid
    )