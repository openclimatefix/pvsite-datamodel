"""Add client table

Revision ID: 31d501a0aa52
Revises: 34891d466985
Create Date: 2024-09-13 11:54:12.743980

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '31d501a0aa52'
down_revision = '34891d466985'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('clients',
        sa.Column('client_uuid', sa.UUID(), nullable=False),
        sa.Column('client_name', sa.String(length=255), nullable=False),
        sa.Column('created_utc', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('client_uuid')
    )
    op.create_index(op.f('ix_clients_client_name'), 'clients', ['client_name'], unique=True)
    op.add_column('sites', sa.Column('client_uuid', sa.UUID(), nullable=True, comment='The UUID of the client this site belongs to'))
    op.create_index(op.f('ix_sites_client_uuid'), 'sites', ['client_uuid'], unique=False)
    op.create_foreign_key(None, 'sites', 'clients', ['client_uuid'], ['client_uuid'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'sites', type_='foreignkey')
    op.drop_index(op.f('ix_sites_client_uuid'), table_name='sites')
    op.drop_column('sites', 'client_uuid')
    op.drop_index(op.f('ix_clients_client_name'), table_name='clients')
    op.drop_table('clients')
    # ### end Alembic commands ###
