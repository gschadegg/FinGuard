from datetime import datetime, timedelta, timezone

import jwt
from passlib.context import CryptContext

from app.auth_settings import AuthSettings, get_auth_settings
from app.config import get_settings
from app.db_interfaces import UserRepo
from app.domain.entities import UserEntity
from app.domain.errors import ConflictError, UnauthorizedError

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

settings = get_settings()


class AuthService:
    def __init__(self, user_repo: UserRepo, settings: AuthSettings | None = None):
        self.user_repo = user_repo
        self.settings = settings or get_auth_settings()

    def _hash(self, password: str) -> str:
        return pwd_context.hash(password)

    def _verify(self, password: str, password_hash: str) -> bool:
        return pwd_context.verify(password, password_hash)

    def _create_access_token(self, *, sub: str, user_id: int) -> str:
        now = datetime.now(timezone.utc)
        exp = now + timedelta(minutes=self.settings.ACCESS_TOKEN_EXPIRE_MIN)

        payload = {
            "sub": sub, 
            "uid": user_id, 
            "iat": int(now.timestamp()), 
            "exp": int(exp.timestamp())
        }

        return jwt.encode(payload, self.settings.SECRET_KEY, algorithm=self.settings.ALGORITHM)

    async def register(self, *, email: str, name: str, password: str):

        if await self.user_repo.get_by_email(email):
            raise ConflictError("Email already exists")
        ph = self._hash(password)
        user = await self.user_repo.add(UserEntity(email=email, name=name), ph)
        token = self._create_access_token(sub=email, user_id=user.id)
        return user, token

    async def login(self, *, email: str, password: str):
        row = await self.user_repo._get_by_email(email)
        if not row or not self._verify(password, row.password_hash):
            raise UnauthorizedError("Invalid email or password")
        

        user = UserEntity(id=row.id, email=row.email, name=row.name)
        token = self._create_access_token(sub=row.email, user_id=row.id)
        return user, token