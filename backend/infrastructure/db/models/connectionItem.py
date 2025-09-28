from sqlalchemy import String, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..base import Base

from datetime import datetime, timezone
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .account import Account

# A user's consented connection to 1 financial institution
class ConnectionItem(Base):
    __tablename__ = "connection_items"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # key to users.id
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    institution_id:   Mapped[str | None] = mapped_column(String(64), index=True, default=None)
    institution_name: Mapped[str | None] = mapped_column(String(128), default=None)

    plaid_item_id: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    access_token_encrypted: Mapped[str] = mapped_column(String(1024))
    transactions_cursor = mapped_column(String(256), nullable=True, index=True)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda:datetime.now(timezone.utc)
    )

    accounts: Mapped[list["Account"]] = relationship(
        back_populates="item", cascade="all, delete-orphan", lazy="selectin", # think I can do this or eager load per query? look into
    )
