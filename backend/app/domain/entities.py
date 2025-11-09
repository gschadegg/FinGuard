from datetime import datetime
from decimal import Decimal
from typing import List, Optional, Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field

# Domain Models for service layer use

# User Class
class UserEntity(BaseModel):
    id: Optional[int] = None
    email: EmailStr
    name: str

    model_config = ConfigDict(from_attributes=True)


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

    transactions_cursor: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)



class TransactionEntity(BaseModel):
    id: int
    account_id: int
    item_id: int
    user_id: int

    plaid_transaction_id: str
    pending_transaction_id: str | None = None

    name: str | None = None
    merchant_name: str | None = None
    amount: float
    iso_currency_code: str | None = None
    date: datetime
    authorized_date: datetime | None = None
    pending: bool
    category: str | None = None
    category_id: str | None = None
    payment_channel: str | None = None

    user_category: str | None = None
    notes: str | None = None


    fraud_score: float | None = None
    is_fraud_suspected: bool = False
    risk_level: str | None = None
    fraud_review_status: Literal["pending", "fraud", "not_fraud", "ignored"] | None = None

    removed: bool = False
    budget_category_id: int | None = None
    budget_category_name: str | None = None

    model_config = ConfigDict(from_attributes=True)


class TransactionsPageEntity(BaseModel):
    items: list[TransactionEntity]
    next_cursor: str | None = None
    has_more: bool = False


class BudgetCategoryEntity(BaseModel):
    id: int
    name: str
    allotted_amount: Decimal
    group: str
    created_at: datetime
    updated_at: datetime | None

    model_config = dict(from_attributes=True)