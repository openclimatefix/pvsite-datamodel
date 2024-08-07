"""Add ml models table

Revision ID: 34891d466985
Revises: fb27362e3b6b
Create Date: 2024-08-07 12:26:23.631105

"""
import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "34891d466985"
down_revision = "fb27362e3b6b"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "ml_model",
        sa.Column(
            "model_uuid", sa.UUID(), server_default=sa.text("gen_random_uuid()"), nullable=False
        ),
        sa.Column("name", sa.String(), nullable=True),
        sa.Column("version", sa.String(), nullable=True),
        sa.Column("created_utc", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("model_uuid"),
    )
    op.add_column(
        "forecast_values",
        sa.Column(
            "ml_model_uuid",
            sa.UUID(),
            nullable=True,
            comment="The ML Model this forcast value belongs to",
        ),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("forecast_values", "ml_model_uuid")
    op.drop_table("ml_model")
    # ### end Alembic commands ###
