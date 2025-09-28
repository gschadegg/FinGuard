from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict, Field
from app.domain.entities import AccountEntity, FullAccountEntity
from app.services_container import get_account_service
from app.services.account_service import AccountService


router = APIRouter(prefix="/accounts", tags=["accounts"])



@router.get("", response_model=List[FullAccountEntity])
async def get_all_accounts(
    user_id: int, 
    selected: Optional[bool] = True, 
    svc: AccountService = Depends(get_account_service)):

    try:
        return await svc.list_all_user_accounts(
            user_id=user_id,
            selected=selected,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@router.get("/{account_id}", response_model=FullAccountEntity)
async def get_account(
    account_id: Optional[int] = None, 
    plaid_account_id: Optional[str] = None,
    svc: AccountService = Depends(get_account_service)):

    try:
        return await svc.get_account_by_id(
            account_id=account_id, 
            plaid_account_id=plaid_account_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))