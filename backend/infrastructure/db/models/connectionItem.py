from sqlalchemy import String, ForeignKey, DateTime, UniqueConstraint, Index, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..base import Base

from datetime import datetime, timezone

# A user's consented connection to 1 financial institution
class ConnectionItem(Base):
    __tablename__ = "connection_items"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # key to users.id
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)

    plaid_item_id: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    access_token_encrypted: Mapped[str] = mapped_column(String(1024))

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.now(timezone.utc)
    )

    accounts: Mapped[list["Account"]] = relationship(
        back_populates="item", cascade="all, delete-orphan"
    )
