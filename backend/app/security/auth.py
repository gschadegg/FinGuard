from fastapi import Depends, HTTPException, status
# from fastapi.security import OAuth2PasswordBearer
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

import jwt
from jwt import InvalidTokenError, ExpiredSignatureError

from app.auth_settings import get_auth_settings, AuthSettings 
from app.services.user_service import UserService
from infrastructure.db.session import get_db
from infrastructure.db.repos.user_repo import SqlUserRepo

bearer_scheme = HTTPBearer(auto_error=True)

async def get_user_service(db=Depends(get_db)) -> UserService:
    return UserService(SqlUserRepo(db))

async def get_current_user(
    token: HTTPAuthorizationCredentials  = Depends(bearer_scheme),
    settings: AuthSettings = Depends(get_auth_settings),
    user_svc: UserService = Depends(get_user_service),
):
    credential_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        token = token.credentials
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        uid = payload.get("uid")
        if uid is None:
            raise credential_exception
    except (ExpiredSignatureError, InvalidTokenError):
        raise credential_exception

    try:
        user = await user_svc.get_user(uid)
        if not user:
            raise credential_exception
        return user
    except Exception:
        raise credential_exception