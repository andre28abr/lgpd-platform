"""anonimizacao de usuario

Revision ID: a2e6c9d1f4b7
Revises: f1d4b8c2a6e5
Create Date: 2026-09-10 18:00:00.000000

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = 'a2e6c9d1f4b7'
down_revision = 'f1d4b8c2a6e5'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('usuarios', schema=None) as batch_op:
        batch_op.add_column(sa.Column('anonimizado_em', sa.DateTime(), nullable=True))


def downgrade():
    with op.batch_alter_table('usuarios', schema=None) as batch_op:
        batch_op.drop_column('anonimizado_em')
