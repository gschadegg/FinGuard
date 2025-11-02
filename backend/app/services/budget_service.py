from decimal import Decimal

from fastapi import HTTPException

from app.db_interfaces import BudgetCategoryRepo

ALLOWED_GROUPS = {"Expenses", "Entertainment", "Savings"}

class BudgetService:
    def __init__(self, budget_repo: BudgetCategoryRepo):
        self.budget_repo = budget_repo

    async def list_categories(self, user_id: int):
        return await self.budget_repo.list_by_user(user_id)


    async def create_category(self, user_id: int, name: str, allotted_amount: Decimal, group: str):

        if group not in ALLOWED_GROUPS:
            raise HTTPException(422, "Invalid group.")
                                
        if await self.budget_repo.get_by_name(user_id, name):
            raise HTTPException(409, "Category with that name already exists.")
        
        return await self.budget_repo.create(user_id, name, allotted_amount, group)


    async def update_category(
            self, 
            user_id: int, 
            category_id: int, 
            *, 
            name: str | None, 
            allotted_amount: Decimal | None, 
            group: str | None
        ):

        if name:
            found = await self.budget_repo.get_by_name(user_id, name)
            if found and found.id != category_id:
                raise HTTPException(409, "Category with that name already exists.")
            
        patch = {}
        if name is not None: 
            patch["name"] = name

        if allotted_amount is not None: 
            patch["allotted_amount"] = allotted_amount

        if group is not None:
            if group not in ALLOWED_GROUPS:
                raise HTTPException(422, "Invalid group.")
            patch["group"] = group

        try:
            return await self.budget_repo.update(user_id, category_id, patch)
        except ValueError:
            raise HTTPException(404, "Category not found.")



    async def delete_category(self, user_id: int, category_id: int):
        try:
            await self.budget_repo.delete(user_id, category_id)
            return {"ok": True}
        
        except Exception:
            raise HTTPException(404, "Category not found.")
