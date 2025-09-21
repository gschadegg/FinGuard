from fastapi import APIRouter, Depends, HTTPException, status
from app.domain.errors import NotFoundError, ConflictError

from app.services_container import get_plaid_service
from app.services.plaid_service import PlaidService
from pydantic import BaseModel
router = APIRouter(prefix="/plaid", tags=["plaid"])

class LinkTokenBody(BaseModel):
    user_id: str

class ExchangeBody(BaseModel):
    public_token: str
    selected_accounts: list[dict] = []


@router.post("/token/create")# response_model
async def create_link(body: LinkTokenBody, svc: PlaidService = Depends(get_plaid_service)):
    try:
        return await svc.create_link_token(user_id=body.user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/token/exchange") # response_model
async def exchange_token(body:ExchangeBody, svc: PlaidService = Depends(get_plaid_service)):
    try:
        return await svc.exchange_public_token(
            public_token=body.public_token, 
            selected_accounts=body.selected_accounts,
            user_id='1')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@router.get("/health")
async def health():
    return {"ok": True}