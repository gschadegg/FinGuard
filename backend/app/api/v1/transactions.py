from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from app.domain.entities import (
    TransactionsPageEntity,
)
from app.security.auth import get_current_user
from app.services.transaction_service import TransactionService
from app.services_container import get_transaction_service


class AssignCategoryBody(BaseModel):
    category_id: Optional[int] = None

router = APIRouter(
    prefix="/transactions", 
    tags=["transactions"], 
    dependencies=[Depends(get_current_user)]
)


# sync transactions by connection item
@router.post("/connection/{item_id}/sync")
async def sync_connection_item_transactions(
    item_id: int, 
    svc: TransactionService = Depends(get_transaction_service),
    current_user = Depends(get_current_user)
):
    res = await svc.sync_connection_item(item_id, user_id=current_user.id)
    if not res.get("ok"):
        raise HTTPException(404, res.get("reason", "unknown"))
    return res



# sync transactions by user
@router.post("/users/sync")
async def sync_user_transactions( 
                                 svc: TransactionService = Depends(get_transaction_service),
                                 current_user = Depends(get_current_user)):
    return await svc.sync_user(current_user.id)


# get all user transactions, paginated
@router.get("", response_model=TransactionsPageEntity)
async def list_user_transactions(
    start: Optional[date] = Query(None),
    end: Optional[date] = Query(None),
    selected: bool = Query(True, description="only accounts marked selected / active"),
    limit: int = Query(50, ge=1, le=200),
    cursor: Optional[str] = Query(None),
    refresh: bool = Query(False, description="if true, sync all user items before listing"),
    svc: TransactionService = Depends(get_transaction_service),
    current_user = Depends(get_current_user)
):
    if refresh:
        await svc.sync_user(current_user.id)
    return await svc.list_user(current_user.id, start, end, 
                               selected_only=selected, limit=limit, cursor=cursor)


# getting transactions by account id, paginated
@router.get("/accounts/{account_id}", response_model=TransactionsPageEntity)
async def list_account_transactions(
    account_id: int,
    start: Optional[date] = Query(None),
    end: Optional[date] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    cursor: Optional[str] = Query(None),
    refresh: bool = Query(False, description="if true, sync this item before listing"),
    svc: TransactionService = Depends(get_transaction_service),
    current_user = Depends(get_current_user)
):
    if refresh:
        found_account = await svc.account_repo.get_one(account_id=account_id, plaid_account_id=None)
        if not found_account:
            raise HTTPException(status_code=404, detail="Account not found")
        
        await svc.sync_connection_item(found_account.item_id, user_id=current_user.id)

    return await svc.list_account(
        account_id, 
        start, 
        end, 
        user_id=current_user.id, 
        limit=limit, 
        cursor=cursor
    )


@router.put("/{transaction_id}/category")
async def assign_transaction_category(
    transaction_id: int,
    body: AssignCategoryBody,
    svc: TransactionService = Depends(get_transaction_service),
    current_user = Depends(get_current_user),
):
    return await svc.assign_category(
        user_id=current_user.id,
        transaction_id=transaction_id,
        category_id=body.category_id,
    )
