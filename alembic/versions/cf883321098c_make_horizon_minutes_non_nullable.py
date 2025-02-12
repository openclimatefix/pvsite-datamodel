"""Make horizon_minutes non-nullable

Revision ID: cf883321098c
Revises: fa74fbe945fd
Create Date: 2025-02-12 12:27:50.030326

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'cf883321098c'
down_revision = 'fa74fbe945fd'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('forecast_values', 'horizon_minutes',
               existing_type=sa.INTEGER(),
               nullable=False,
               existing_comment='The time difference between the creation time of the forecast value and the start of the time interval it applies for')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('forecast_values', 'horizon_minutes',
               existing_type=sa.INTEGER(),
               nullable=True,
               existing_comment='The time difference between the creation time of the forecast value and the start of the time interval it applies for')
    # ### end Alembic commands ###
