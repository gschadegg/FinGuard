from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth_settings import AuthSettings, get_auth_settings
from app.config import get_settings
from app.services.account_service import AccountService
from app.services.auth_service import AuthService
from app.services.budget_service import BudgetService
from app.services.fraud_detection_service import FraudDetectionService
from app.services.plaid_service import PlaidService
from app.services.transaction_service import TransactionService
from app.services.user_service import UserService
from app.services.dashboard_service import DashboardService

from infrastructure.db.repos.account_repo import SqlAccountRepo
from infrastructure.db.repos.budget_category_repo import SqlBudgetCategoryRepo
from infrastructure.db.repos.connectionItem_repo import SqlConnectionItemRepo
from infrastructure.db.repos.transaction_repo import SqlTransactionRepo
from infrastructure.db.repos.user_repo import SqlUserRepo
from infrastructure.db.session import SessionLocal, get_db

settings = get_settings()



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

async def get_auth_service(
        settings: AuthSettings = Depends(get_auth_settings),
        db: AsyncSession = Depends(get_db), 
    ) -> AuthService:
    user_repo = SqlUserRepo(db)
    settings = settings
    return AuthService(
        user_repo=user_repo,
        settings = settings
    )


async def get_fraud_detection_service(
        db: AsyncSession = Depends(get_db)
    ) -> FraudDetectionService:

    return FraudDetectionService(
        # uses background service to run in tandem so need SessionLocal
        session_factory=SessionLocal,
        # transaction_repo=transaction_repo,
        model_path="fraud_detection/fraud_model.joblib",
        enabled=True,
        
    ) 

async def get_transaction_service(
        db: AsyncSession = Depends(get_db), 
        plaid: PlaidService = Depends(get_plaid_service),
        fraud_detection_svc: FraudDetectionService = Depends(get_fraud_detection_service)
    ) -> TransactionService:
    
    account_repo = SqlAccountRepo(db)
    connection_item_repo = SqlConnectionItemRepo(db)
    transaction_repo = SqlTransactionRepo(db)
    budget_category_repo = SqlBudgetCategoryRepo(db)

    return TransactionService(
        account_repo=account_repo, 
        connection_item_repo=connection_item_repo, 
        transaction_repo=transaction_repo,
        plaid=plaid,
        budget_category_repo=budget_category_repo,
        fraud_detection_svc=fraud_detection_svc
    )


async def get_budget_service(
        db: AsyncSession = Depends(get_db)
    ) -> BudgetService:

    repo = SqlBudgetCategoryRepo(db)
    return BudgetService(repo)


async def get_dashboard_service(
        db: AsyncSession = Depends(get_db),
        account_svc: AccountService = Depends(get_account_service),
        budget_svc: BudgetService = Depends(get_budget_service),
        transaction_svc: TransactionService = Depends(get_transaction_service),
    ) -> DashboardService:

    return DashboardService(
        account_svc=account_svc,
        budget_svc= budget_svc,
        transaction_svc=transaction_svc
    )