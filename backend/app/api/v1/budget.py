from decimal import Decimal
from typing import Literal

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.domain.entities import BudgetCategoryEntity
from app.security.auth import get_current_user
from app.services.budget_service import BudgetService
from app.services_container import get_budget_service


class BudgetCategoryCreate(BaseModel):
    name: str = Field(min_length=1, max_length=64)
    allotted_amount: Decimal = Field(ge=0)
    group: Literal["Expenses", "Entertainment", "Savings"]

class BudgetCategoryUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=64)
    allotted_amount: Decimal | None = Field(default=None, ge=0)
    group: Literal["Expenses", "Entertainment", "Savings"] | None = None


router = APIRouter(
    prefix="/budgets",
    tags=["budgets"],
    dependencies=[Depends(get_current_user)]
)




@router.get("/categories")
async def list_categories(
    svc: BudgetService = Depends(get_budget_service),
    current_user = Depends(get_current_user),
):
    category_info = await svc.list_categories(current_user.id)
    return {"ok": True, **category_info}



@router.post("/categories", response_model=BudgetCategoryEntity, status_code=201)
async def create_category(
    body: BudgetCategoryCreate,
    svc: BudgetService = Depends(get_budget_service),
    current_user = Depends(get_current_user),
):
    return await svc.create_category(current_user.id, body.name, body.allotted_amount, body.group)


@router.patch("/categories/{category_id}", response_model=BudgetCategoryEntity)
async def update_category(
    category_id: int,
    body: BudgetCategoryUpdate,
    svc: BudgetService = Depends(get_budget_service),
    current_user = Depends(get_current_user),
):
    return await svc.update_category(
        current_user.id,
        category_id,
        name=body.name,
        allotted_amount=body.allotted_amount,
        group=body.group
    )

@router.delete("/categories/{category_id}")
async def delete_category(
    category_id: int,
    svc: BudgetService = Depends(get_budget_service),
    current_user = Depends(get_current_user),
):
    return await svc.delete_category(current_user.id, category_id)

