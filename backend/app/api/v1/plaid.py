from typing import List, Literal, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict, Field

from app.security.auth import get_current_user
from app.services.plaid_service import PlaidService
from app.services_container import get_plaid_service

router = APIRouter(prefix="/plaid", tags=["plaid"], dependencies=[Depends(get_current_user)])

class LinkTokenBody(BaseModel):
    user_id: int
    mode: Literal["create","update"] = "create"
    plaid_item_id: Optional[str] = None

class TokenBody(BaseModel):
    plaid_item_id: str

class AccountBodyEntity(BaseModel):
    plaid_account_id: str = Field(alias="id")
    name: Optional[str] = None
    mask: Optional[str] = None
    type: Optional[str] = None
    subtype: Optional[str] = None
    selected: Optional[bool] = True
    model_config = ConfigDict(populate_by_name=True)

class InstitutionBody(BaseModel):
    id: str | None = None
    name: str | None = None

class ExchangeBody(BaseModel):
    public_token: str
    selected_accounts: List[AccountBodyEntity] = Field(default_factory=list)
    user_id:int
    institution: InstitutionBody | None = None
    unselect_others: bool = False


@router.post("/token/create")# response_model
async def create_link(body: LinkTokenBody, svc: PlaidService = Depends(get_plaid_service)):
    try:
        return await svc.create_link_token(
            user_id=body.user_id,
            mode=body.mode,
            plaid_item_id=body.plaid_item_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/token/exchange") # response_model
async def exchange_token(body:ExchangeBody, svc: PlaidService = Depends(get_plaid_service)):
    try:
        account_entities = [
            AccountBodyEntity(
                plaid_account_id=account.plaid_account_id, 
                name=account.name,
                mask=account.mask,
                type= account.type,
                subtype= account.subtype,
                selected=True,

            )
            for account in body.selected_accounts
        ]

        return await svc.exchange_public_token(
            public_token=body.public_token, 
            selected_accounts=account_entities,
            user_id=body.user_id,
            institution=body.institution,
            unselect_others=body.unselect_others,
        )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
