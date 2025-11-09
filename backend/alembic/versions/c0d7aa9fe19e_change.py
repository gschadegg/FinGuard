"""change

Revision ID: c0d7aa9fe19e
Revises: f9e1698e1492
Create Date: 2025-11-09 11:00:38.885581

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "c0d7aa9fe19e"
down_revision = "f9e1698e1492"
branch_labels = None
depends_on = None

def upgrade():
    fraud_enum = postgresql.ENUM(
        "pending", "fraud", "not_fraud", "ignored",
        name="fraud_review_status",
        create_type=True,
    )
    fraud_enum.create(op.get_bind(), checkfirst=True)

    op.add_column(
        "transactions",
        sa.Column(
            "fraud_review_status",
            postgresql.ENUM(
                "pending", "fraud", "not_fraud", "ignored",
                name="fraud_review_status",
                create_type=False,
            ),
            nullable=True,
            server_default="pending",
        ),
    )

    op.add_column("transactions", sa.Column("fraud_reviewed_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("transactions", sa.Column("fraud_reviewed_by", sa.Integer(), nullable=True))
    op.add_column("transactions", sa.Column("fraud_review_note", sa.Text(), nullable=True))
    op.create_index("ix_tx_fraud_reviewed_by", "transactions", ["fraud_reviewed_by"])

    op.alter_column("transactions", "fraud_review_status", nullable=False)
    op.alter_column("transactions", "fraud_review_status", server_default=None)


def downgrade():
    op.drop_index("ix_tx_fraud_reviewed_by", table_name="transactions")
    op.drop_column("transactions", "fraud_review_note")
    op.drop_column("transactions", "fraud_reviewed_by")
    op.drop_column("transactions", "fraud_reviewed_at")
    op.drop_column("transactions", "fraud_review_status")

    fraud_enum = postgresql.ENUM(name="fraud_review_status")
    fraud_enum.drop(op.get_bind(), checkfirst=True)