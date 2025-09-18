from typing import Sequence
from app.domain.entities import UserEntity
from app.domain.errors import NotFoundError, ConflictError
from app.db_interfaces import UserRepo

class UserService:
    def __init__(self, repo: UserRepo):
        self.repo = repo

    async def create_user(self, email: str, name: str) -> UserEntity:
        if await self.repo.get_by_email(email):
            raise ConflictError("Email already exists")
        user = UserEntity(email=email, name=name)
        created = await self.repo.add(user)
        return created

    async def get_user(self, user_id: int) -> UserEntity:
        user = await self.repo.get_by_id(user_id)
        if not user:
            raise NotFoundError("User not found")
        return user

    async def list_users(self) -> Sequence[UserEntity]:
        return await self.repo.list()

    async def delete_user(self, user_id: int) -> None:
        # ensure it exists (optional guard)
        if not await self.repo.get_by_id(user_id):
            raise NotFoundError("User not found")
        await self.repo.delete(user_id)