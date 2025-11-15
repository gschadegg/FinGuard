from datetime import date
from decimal import Decimal
from typing import Optional

from app.domain.entities import (
    DashboardAccountSummary,
    DashboardBudgetSummary,
    DashboardCategoryRollup,
    DashboardEntity,
)
from app.services.account_service import AccountService
from app.services.budget_service import BudgetService
from app.services.transaction_service import TransactionService


def _to_decimal(value) -> Decimal:
    if value is None:
        return Decimal("0")
    return Decimal(str(value))


def _get(obj, key: str, default=None):
    if isinstance(obj, dict):
        return obj.get(key, default)
    return getattr(obj, key, default)


class DashboardService:
    def __init__(
        self,
        account_svc: AccountService,
        budget_svc: BudgetService,
        transaction_svc: TransactionService,
    ) -> None:
        self.account_svc = account_svc
        self.budget_svc = budget_svc
        self.transaction_svc = transaction_svc


    async def get_dashboard(
        self,
        user_id: int,
        year: Optional[int] = None,
        month: Optional[int] = None,
        *,
        selected_only: bool = True,
    ) -> DashboardEntity:
        
        # getting relevant time period
        today = date.today()
        year = year or today.year
        month = month or today.month
        period = {
            "year": year,
            "month": month,
            "label": date(year, month, 1).strftime("%B %Y"),
        }


        # getting account data and their balances
        accounts = await self.account_svc.list_all_user_accounts(
            user_id=user_id,
            selected=selected_only,
        )

        account_summaries: list[DashboardAccountSummary] = []
        total_balance = Decimal("0")

        # need to pair down the data and flatten
        for account in accounts:
            balances = getattr(account.plaid, "balances", None) if account.plaid else None
            current = getattr(balances, "current", None) if balances else None
            available = getattr(balances, "available", None) if balances else None

            bal_value = Decimal(str(current or available or 0))
            total_balance += bal_value

            account_summaries.append(
                DashboardAccountSummary(
                    id=account.id,
                    name=(
                        account.plaid.name 
                        if account.plaid and account.plaid.name 
                        else account.name
                    ),
                    mask=(
                        account.plaid.mask 
                        if account.plaid and account.plaid.mask 
                        else account.mask
                    ),
                    type=account.type,
                    subtype=account.subtype,
                    institution_name=account.institution_name,
                    balance=bal_value,
                    available=Decimal(str(available)) if available is not None else None,
                    selected=account.selected,
                )
            )

        totals = total_balance

        ########
        # getting risk data
        risk_rollup = await self.transaction_svc.get_rollups(user_id)

        ########
        # getting budget & category  data
        budget_data = await self.budget_svc.list_categories(
            user_id=user_id,
            year=year,
            month=month,
        )

        # creating defaults for categories and amounts
        categories = budget_data.get("categories") or []

        total_budget = _to_decimal(budget_data.get("total_budgeted", 0))
        total_spent = _to_decimal(budget_data.get("total_spent", 0))
        total_remaining = _to_decimal(
            budget_data.get("total_remaining", total_budget - total_spent)
        )

        budget_summary = DashboardBudgetSummary(
            spent=total_spent,
            budget=total_budget,
            available=total_remaining,
        )

        ########
        # calculate the percentages for spent for each category
        spending_categories: list[DashboardCategoryRollup] = []
        total_spent_for_mix = total_spent if total_spent > 0 else Decimal("0")

        if total_spent_for_mix > 0:
            for category in categories:
                # category is a dict from budget repo
                category_spent = _to_decimal(
                    _get(category, "spent_amount", _get(category, "spent", 0))
                )

                if category_spent <= 0:
                    continue

                percent = float((category_spent / total_spent_for_mix) * Decimal("100"))

                spending_categories.append(
                    DashboardCategoryRollup(
                        category_id=_get(category, "id"),
                        name=_get(category, "name", ""),
                        amount=category_spent,
                        percent=percent,
                    )
                )


        return DashboardEntity(
            period=period, # current or specified time period being summarized
            totals=totals, # total balance of accounts
            risk_data=risk_rollup,  # risk tiers w/ counts and count for each account
            budget=budget_summary, # budget total numbers
            # list of categories and percentage of budget spent
            spending_categories=spending_categories, 
            accounts=account_summaries,  # list of accounts and their details
        )
