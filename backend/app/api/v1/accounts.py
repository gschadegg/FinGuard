from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from app.domain.errors import NotFoundError

from app.domain.entities import FullAccountEntity
from app.security.auth import get_current_user
from app.services.account_service import AccountService
from app.services_container import get_account_service

router = APIRouter(prefix="/accounts", tags=["accounts"], dependencies=[Depends(get_current_user)])



@router.get("", response_model=List[FullAccountEntity])
async def get_all_accounts(
    selected: Optional[bool] = True,
    svc: AccountService = Depends(get_account_service),
    current_user = Depends(get_current_user)):
    
    try:
        return await svc.list_all_user_accounts(
            user_id=current_user.id,
            selected=selected,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@router.get("/{account_id}", response_model=FullAccountEntity)
async def get_account(
    account_id: Optional[int] = None, 
    plaid_account_id: Optional[str] = None,
    svc: AccountService = Depends(get_account_service),
    current_user = Depends(get_current_user)):

    try:
        return await svc.get_account_by_id(
            account_id=account_id, 
            plaid_account_id=plaid_account_id,
            user_id=current_user.id
        )
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))