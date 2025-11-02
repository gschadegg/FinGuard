# infrastructure/db/models.py
from sqlalchemy import String, ForeignKey, DateTime, UniqueConstraint, Index, Boolean, Date, Numeric, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..base import Base
from datetime import datetime, timezone

class BudgetCategory(Base):
    __tablename__ = "budget_categories"
    __table_args__ = (
        UniqueConstraint("user_id", "name", name="uq_budget_category_user_name"),
        Index("ix_budget_categories_user_id", "user_id"),
        CheckConstraint(
            "group IN ('Expenses', 'Entertainment', 'Savings')",
            name="chk_budget_category_group_valid"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)

    name: Mapped[str] = mapped_column(String(64))
    allotted_amount: Mapped[Numeric] = mapped_column(Numeric(18, 2))
    group: Mapped[str] = mapped_column(String(32))

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))