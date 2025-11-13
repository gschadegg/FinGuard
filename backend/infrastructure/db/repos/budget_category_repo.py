
from decimal import Decimal
from sqlalchemy import select, update, delete, func, case
from app.domain.entities import BudgetCategoryEntity
from datetime import date
from typing import Any

from infrastructure.db.models.budgetCategory import BudgetCategory
from infrastructure.db.models.transaction import Transaction
from sqlalchemy.ext.asyncio import AsyncSession


def _to_entity(row: BudgetCategory) -> BudgetCategoryEntity:
    return BudgetCategoryEntity.model_validate(row, from_attributes=True)



class SqlBudgetCategoryRepo:
    def __init__(self, session: AsyncSession):
        self.session = session


    async def create(self, user_id: int, name: str, allotted_amount: Decimal, group: str) -> BudgetCategoryEntity:

        row = BudgetCategory(user_id=user_id, name=name, allotted_amount=allotted_amount, group=group)
        self.session.add(row)

        await self.session.flush()
        await self.session.commit()
        await self.session.refresh(row)

        return _to_entity(row)


    # getting all user owned categories - need to add rolled up info
    async def list_by_user(
            self,
            user_id: int,
            start_date: date | None = None,
            end_date: date | None = None,
        ) -> list[BudgetCategoryEntity]:

        rows = (await self.session.execute(
            select(BudgetCategory)
            .where(BudgetCategory.user_id == user_id)
            .order_by(BudgetCategory.name.asc())
        )).scalars().all()

        categories = [_to_entity(r) for r in rows]

        total_query = await self.session.execute(
            select(func.coalesce(func.sum(BudgetCategory.allotted_amount), 0))
            .where(BudgetCategory.user_id == user_id)
        )
        total_amount = total_query.scalar_one() or Decimal("0")

        spent_transactions = select(
            Transaction.budget_category_id,
            func.coalesce(func.sum(Transaction.amount), 0)
        ).where(
            Transaction.user_id == user_id,
            Transaction.removed.is_(False),
            Transaction.pending.is_(False),
        )

        if start_date:
            spent_transactions = spent_transactions.where(Transaction.date >= start_date)
        if end_date:
            spent_transactions = spent_transactions.where(Transaction.date < end_date)

        spent_transactions = spent_transactions.group_by(Transaction.budget_category_id)

        spending_rows = await self.session.execute(spent_transactions)

        spending_map: dict[int, Decimal] = {
            cat_id: spent or Decimal("0")
            for cat_id, spent in spending_rows
            if cat_id is not None
        }

        # need totals for each category
        category_dicts = []
        total_spent = Decimal("0")

        for category in categories:
            spent = spending_map.get(category.id, Decimal("0"))
            remaining = (category.allotted_amount or Decimal("0")) - spent
            total_spent += spent

            category_dicts.append(
                {
                    **category.model_dump(),
                    "spent_amount": str(spent),
                    "remaining_amount": str(remaining),
                }
            )

        total_remaining = total_amount - total_spent

        return {
            "categories": category_dicts,
            "total_budgeted": str(total_amount),
            "total_spent": str(total_spent),
            "total_remaining": str(total_remaining),
            "period": {
                "start_date": start_date.isoformat() if start_date else None,
                "end_date": end_date.isoformat() if end_date else None,
            },
        }


    

    async def get_by_name(self, user_id: int, name: str) -> BudgetCategoryEntity | None:

        row = (await self.session.execute(
            select(BudgetCategory).where(BudgetCategory.user_id == user_id, BudgetCategory.name == name)
        )).scalar_one_or_none()


        return _to_entity(row) if row else None


    async def update(self, user_id: int, category_id: int, patch: dict) -> BudgetCategoryEntity:
        found_category = (
            update(BudgetCategory)
            .where(BudgetCategory.id == category_id, BudgetCategory.user_id == user_id)
            .values(**patch)
            .returning(BudgetCategory)
        )
        res = await self.session.execute(found_category)
        await self.session.commit()
        row = res.scalar_one_or_none()

        if not row:
            raise ValueError("Category not found")
        
        return _to_entity(row)



    async def delete(self, user_id: int, category_id: int) -> None:
        await self.session.execute(
            update(Transaction)
            .where(Transaction.user_id == user_id, Transaction.budget_category_id == category_id)
            .values(budget_category_id=None)
        )

        await self.session.execute(
            delete(BudgetCategory).where(BudgetCategory.id == category_id, BudgetCategory.user_id == user_id)
        )

        await self.session.flush()
        await self.session.commit()



    async def get_owned(self, user_id: int, category_id: int) -> BudgetCategoryEntity | None:

        row = (await self.session.execute(
            select(BudgetCategory).where(BudgetCategory.id == category_id, BudgetCategory.user_id == user_id)
        )).scalar_one_or_none()

        return _to_entity(row) if row else None