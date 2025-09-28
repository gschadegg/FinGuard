from typing import Iterable, Optional, Protocol, Sequence, Union

from app.domain.entities import ConnectionItemEntity, UserEntity, AccountEntity
# DB Repositories Interfaces


# need to use protocol so anything with same methods counts as class for testing purposes
class UserRepo(Protocol):
    async def get_by_id(self, user_id: int) -> Optional[UserEntity]: ...
    async def get_by_email(self, email: str) -> Optional[UserEntity]: ...
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