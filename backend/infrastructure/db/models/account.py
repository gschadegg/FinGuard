from sqlalchemy import String, ForeignKey, UniqueConstraint, Index, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..base import Base

from infrastructure.db.models.connectionItem import ConnectionItem


# Financial Account
class Account(Base):
    __tablename__ = "accounts"
    __table_args__ = (
        UniqueConstraint("plaid_account_id", name="uq_accounts_plaid_account_id"), # no row can have the same account id
        Index("ix_accounts_item_id", "item_id"), # supposed to help with query speeds when joining/fetching connection items
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # key to connection_items.id
    item_id: Mapped[int] = mapped_column(ForeignKey("connection_items.id", ondelete="CASCADE"))

    plaid_account_id: Mapped[str] = mapped_column(String(128), index=True)
    name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    mask: Mapped[str | None] = mapped_column(String(10), nullable=True)
    type: Mapped[str | None] = mapped_column(String(50), nullable=True) # account types like depository/credit/loan
    subtype: Mapped[str | None] = mapped_column(String(50), nullable=True) # account types like checking/savings
    selected: Mapped[bool] = mapped_column(Boolean, default=True) # if there is a connection item for it/selected by user


    item: Mapped["ConnectionItem"] = relationship(back_populates="accounts")
