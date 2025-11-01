from sqlalchemy import String, ForeignKey, DateTime, UniqueConstraint, Index, Boolean, Date, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..base import Base

from datetime import datetime, timezone, date
from typing import TYPE_CHECKING


class Transaction(Base):
    __tablename__ = "transactions"
    __table_args__ = (
        UniqueConstraint("plaid_transaction_id", name="uq_transactions_plaid_id"),
        Index("ix_tx_account_date_id", "account_id", "date", "id"),
        Index("ix_tx_user_date_id", "user_id", "date", "id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # keys to other tables
    account_id: Mapped[int] = mapped_column(ForeignKey("accounts.id", ondelete="CASCADE"), index=True)
    item_id:    Mapped[int] = mapped_column(ForeignKey("connection_items.id", ondelete="CASCADE"), index=True)
    user_id:    Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)

    # Plaid ids
    plaid_transaction_id: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    pending_transaction_id: Mapped[str | None] = mapped_column(String(128), nullable=True, index=True)

    name: Mapped[str | None] = mapped_column(String(256))
    merchant_name: Mapped[str | None] = mapped_column(String(256))
    amount: Mapped[Numeric] = mapped_column(Numeric(18, 2))
    iso_currency_code: Mapped[str | None] = mapped_column(String(8))
    date: Mapped[datetime] = mapped_column(Date)
    authorized_date: Mapped[datetime | None] = mapped_column(Date)
    pending: Mapped[bool] = mapped_column(Boolean, default=False)
    category: Mapped[str | None] = mapped_column(String(256))
    category_id: Mapped[str | None] = mapped_column(String(64))
    payment_channel: Mapped[str | None] = mapped_column(String(32))


    # app updated fields
    user_category: Mapped[str | None] = mapped_column(String(64))
    notes: Mapped[str | None] = mapped_column(String(512))
    fraud_score: Mapped[float | None]
    is_fraud_suspected: Mapped[bool] = mapped_column(Boolean, default=False)

    removed: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    budget_category_id: Mapped[int | None] = mapped_column(
        ForeignKey("budget_categories.id", ondelete="SET NULL"), index=True, nullable=True
    )