from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field

# Domain Models for service layer use

# User Class
class UserEntity(BaseModel):
    id: Optional[int] = None
    email: EmailStr
    name: str

class AccountEntity(BaseModel):
    id: Optional[int] = None
    item_id: int
    plaid_account_id: str
    name: Optional[str] = None
    mask: Optional[str] = None
    type: Optional[str] = None
    subtype: Optional[str] = None
    selected: bool = True
    institution_id: Optional[str] = None
    institution_name: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class PlaidBalancesEntity(BaseModel):
    available: Optional[float] = None
    current: Optional[float] = None
    iso_currency_code: Optional[str] = None
    unofficial_currency_code: Optional[str] = None


class PlaidAccountViewEntity(BaseModel):
    account_id: str
    name: Optional[str] = None
    official_name: Optional[str] = None
    mask: Optional[str] = None
    type: Optional[str] = None
    subtype: Optional[str] = None
    verification_status: Optional[str] = None
    balances: Optional[PlaidBalancesEntity] = None


class FullAccountEntity(BaseModel):
    id: int
    item_id: int
    plaid_account_id: str
    name: Optional[str] = None
    mask: Optional[str] = None
    type: Optional[str] = None
    subtype: Optional[str] = None
    selected: bool = True
    institution_id: Optional[str] = None
    institution_name: Optional[str] = None

    #plaid fetched details
    plaid: Optional[PlaidAccountViewEntity] = None

    
class ConnectionItemEntity(BaseModel):
    id: Optional[int] = None
    user_id: int
    plaid_item_id: str
    access_token_encrypted: str
    created_at: Optional[datetime] = None
    accounts: List[AccountEntity] = Field(default_factory=list)

    institution_id: Optional[str] = None 
    institution_name: Optional[str] = None 
    model_config = ConfigDict(from_attributes=True)