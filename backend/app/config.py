import os
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict

ENV = os.getenv("ENV", "dev")

def _env_file_for(env: str) -> str:
    mapping = {"dev": ".env.dev", "prod": ".env.prod"}
    return mapping.get(env, ".env.dev")

class Settings(BaseSettings):
    ENV: str = ENV
    API_BASE_URL: str
    DATABASE_URL: str
    DATABASE_URL_SYNC: str | None = None
    PLAID_CLIENT_ID: str
    PLAID_SECRET: str
    PLAID_ENCRYPT_KEY: str
    AUTH_SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MIN: int
    # need to add each env variable expected if want to include and have access to it

    model_config = SettingsConfigDict(
        env_file=_env_file_for(ENV), 
        extra="ignore", 
        env_file_encoding="utf-8", 
        case_sensitive=False,
    )


    # not sure if these will need to be different /same with the packages being used, 
    # might need to do research as things develop
    @property
    def async_db_url(self) -> str:
        return self.DATABASE_URL

    @property
    def sync_db_url(self) -> str:
        return self.DATABASE_URL_SYNC or self.DATABASE_URL

@lru_cache
def get_settings() -> Settings:
    return Settings()