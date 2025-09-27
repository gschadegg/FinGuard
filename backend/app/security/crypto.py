import os
from cryptography.fernet import Fernet
from app.config import Settings, get_settings

settings = get_settings()

key = settings.PLAID_ENCRYPT_KEY

if not key:
    raise RuntimeError("There is no encryption key, generate one and set it in env")
fernet = Fernet(key.encode() if isinstance(key, str) else key)

def encrypt(txt: str) -> str:
    return fernet.encrypt(txt.encode()).decode()

def decrypt(token: str) -> str:
    return fernet.decrypt(token.encode()).decode()