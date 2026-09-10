"""auditoria encadeada por hash e remetente de e-mail por empresa

Revision ID: c7a1e5b2d9f0
Revises: eaedbce82aff
Create Date: 2026-09-10 10:00:00.000000

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = 'c7a1e5b2d9f0'
down_revision = 'eaedbce82aff'
branch_labels = None
depends_on = None


def upgrade():
    # Colunas nulas: não exigem server_default no SQLite (modo batch) nem no Postgres.
    with op.batch_alter_table('audit_logs', schema=None) as batch_op:
        batch_op.add_column(sa.Column('hash', sa.String(length=64), nullable=True))

    with op.batch_alter_table('empresas', schema=None) as batch_op:
        batch_op.add_column(sa.Column('email_remetente', sa.String(length=255), nullable=True))


def downgrade():
    with op.batch_alter_table('empresas', schema=None) as batch_op:
        batch_op.drop_column('email_remetente')

    with op.batch_alter_table('audit_logs', schema=None) as batch_op:
        batch_op.drop_column('hash')
