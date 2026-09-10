"""protocolo publico e origem do pedido do titular

Revision ID: e9c3a7b5d2f1
Revises: d8b2f4a6c1e3
Create Date: 2026-09-10 14:00:00.000000

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = 'e9c3a7b5d2f1'
down_revision = 'd8b2f4a6c1e3'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('pedidos_titular', schema=None) as batch_op:
        batch_op.add_column(sa.Column('protocolo', sa.String(length=20), nullable=True))
        batch_op.add_column(sa.Column('origem', sa.String(length=20), nullable=True))
        batch_op.create_index(batch_op.f('ix_pedidos_titular_protocolo'), ['protocolo'], unique=True)


def downgrade():
    with op.batch_alter_table('pedidos_titular', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_pedidos_titular_protocolo'))
        batch_op.drop_column('origem')
        batch_op.drop_column('protocolo')
