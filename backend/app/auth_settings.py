from functools import lru_cache
from app.config import get_settings 

class AuthSettings:
    def __init__(self):
        cfg = get_settings()
        self.SECRET_KEY = cfg.AUTH_SECRET_KEY
        self.ALGORITHM = "HS256"
        self.ACCESS_TOKEN_EXPIRE_MIN = cfg.ACCESS_TOKEN_EXPIRE_MIN

@lru_cache
def get_auth_settings() -> AuthSettings:
    return AuthSettings()
