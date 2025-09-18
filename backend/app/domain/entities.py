from pydantic import BaseModel, EmailStr
from typing import Optional

# Domain Models for service layer use

# User Class
class UserEntity(BaseModel):
    id: Optional[int] = None
    email: EmailStr
    name: str

