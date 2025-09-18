import pytest
from typing import Optional, Sequence, List
from app.services.user_service import UserService
from app.domain.entities import UserEntity
from app.domain.errors import NotFoundError, ConflictError

# this is an example to figure out the structure and workflow I want to follow
# need to mock the each db repo and pas to the service being tested to prevent tests hitting db
class FakeUserRepo:
    def __init__(self):
        self.rows: List[UserEntity] = []
        self._id = 0

    async def get_by_id(self, user_id: int) -> Optional[UserEntity]:
        for r in self.rows:
            if r.id == user_id:
                return r
        return None

    async def get_by_email(self, email: str) -> Optional[UserEntity]:
        return next((r for r in self.rows if r.email == email), None)

    async def list(self) -> Sequence[UserEntity]:
        return list(self.rows)

    async def add(self, user: UserEntity) -> UserEntity:
        self._id += 1
        created = UserEntity(id=self._id, email=user.email, name=user.name)
        self.rows.append(created)
        return created

    async def delete(self, user_id: int) -> None:
        self.rows = [r for r in self.rows if r.id != user_id]

@pytest.mark.anyio
async def test_create_and_get_user():
    svc = UserService(repo=FakeUserRepo())
    created = await svc.create_user("a@b.com", "Alice")
    assert created.id == 1
    got = await svc.get_user(1)
    assert got.email == "a@b.com"

@pytest.mark.anyio
async def test_duplicate_email():
    svc = UserService(repo=FakeUserRepo())
    await svc.create_user("a@b.com", "Alice")
    with pytest.raises(ConflictError):
        await svc.create_user("a@b.com", "Again")