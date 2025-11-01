from datetime import date
from typing import Iterable, Optional, Protocol, Sequence, Union
from decimal import Decimal

from app.domain.entities import AccountEntity, ConnectionItemEntity, UserEntity, BudgetCategoryEntity
from infrastructure.db.models import User

# DB Repositories Interfaces


# need to use protocol so anything with same methods counts as class for testing purposes
class UserRepo(Protocol):
    async def get_by_id(self, user_id: int) -> Optional[UserEntity]: ...
    async def get_by_email(self, email: str) -> Optional[UserEntity]: ...
    async def _get_by_email(self, email: str) -> Optional[User]: ...
    async def list(self) -> Sequence[UserEntity]: ...
    async def add(self, user: UserEntity) -> UserEntity: ...
    async def delete(self, user_id: int) -> None: ...



# Plaid Financial Accounts
class AccountRepo(Protocol):
    async def upsert_selected(
            self, 
            item_id: int, 
            selectedAccount: Iterable[dict], 
            unselect_others: bool,
            institution_id: Optional[str] = None,
            institution_name: Optional[str] = None,
        ) -> None: ...
    
    async def list_by_user_id(
        self,
        user_id: int,
        only_selected: Optional[bool] = True,
    ) -> list[AccountEntity]: ...
    
    async def get_one(
        self,
        *,
        account_id: Optional[int] = None,
        plaid_account_id: Optional[str] = None,
    ) -> Optional[AccountEntity]: ...


class ConnectionItemRepo(Protocol):
    async def get_by_connection_item_id(self, plaid_item_id: str) -> ConnectionItemEntity | None: 
        ...
    async def get_by_id(self, id: int) -> ConnectionItemEntity | None: ... 
    async def add(self, item: ConnectionItemEntity) -> ConnectionItemEntity: ... 
    async def update(self,
        item_or_entity: Union[int, str, ConnectionItemEntity], 
        token_encrypted: str,
        institution_id: Optional[str] = None,
        institution_name: Optional[str] = None) -> ConnectionItemEntity:...
    async def list_ids_by_user(self, user_id: int) -> list[int]: ...
    async def update_transactions_cursor(self, item_id: int, cursor: str | None) -> None: ...


class TransactionRepo(Protocol):
    async def upsert_from_plaid(self, item: ConnectionItemEntity, plaid_tx: dict) -> int: ...
    async def mark_removed(self, plaid_ids: list[str]) -> None: ...
    async def list_by_user_paginated(
            self, 
            user_id: int, 
            start_date: date | None, 
            end_date: date | None,
            *, 
            selected_only: bool, 
            limit: int, 
            cursor: str | None
    ) -> dict: ...
    async def list_by_account_paginated(
            self, 
            account_id: int, 
            start_date: date | None, 
            end_date: date | None,
            *, 
            limit: int, 
            cursor: str | None
    ) -> dict: ...



class BudgetCategoryRepo(Protocol):
    async def get_by_name(self, user_id: int, name: str) -> BudgetCategoryEntity | None: ...
    async def list_by_user(self, user_id: int) -> list[BudgetCategoryEntity]: ...
    async def create(self, user_id: int, name: str, allotted_amount) -> BudgetCategoryEntity: ...
    async def update(self, user_id: int, category_id: int, patch: dict) -> BudgetCategoryEntity: ...
    async def delete(self, user_id: int, category_id: int) -> None: ...
    