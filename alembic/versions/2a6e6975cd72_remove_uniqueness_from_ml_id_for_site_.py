"""Remove uniqueness from ml id for site table

Revision ID: 2a6e6975cd72
Revises: 34891d466985
Create Date: 2024-09-20 15:23:59.973409

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "2a6e6975cd72"
down_revision = "34891d466985"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column(
        "sites",
        "ml_id",
        existing_type=sa.INTEGER(),
        comment="Auto-incrementing integer ID of the site for use in ML training",
        existing_nullable=False,
        autoincrement=True,
    )
    op.drop_constraint("sites_ml_id_key", "sites", type_="unique")
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint("sites_ml_id_key", "sites", ["ml_id"])
    op.alter_column(
        "sites",
        "ml_id",
        existing_type=sa.INTEGER(),
        comment=None,
        existing_comment="Auto-incrementing integer ID of the site for use in ML training",
        existing_nullable=False,
        autoincrement=True,
    )
    # ### end Alembic commands ###
