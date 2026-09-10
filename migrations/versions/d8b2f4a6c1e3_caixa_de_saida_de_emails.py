"""caixa de saida de e-mails

Revision ID: d8b2f4a6c1e3
Revises: c7a1e5b2d9f0
Create Date: 2026-09-10 12:00:00.000000

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = 'd8b2f4a6c1e3'
down_revision = 'c7a1e5b2d9f0'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'emails_enviados',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('empresa_id', sa.Integer(), nullable=True),
        sa.Column('remetente', sa.String(length=255), nullable=True),
        sa.Column('destinatario', sa.String(length=255), nullable=False),
        sa.Column('assunto', sa.String(length=255), nullable=False),
        sa.Column('corpo', sa.Text(), nullable=True),
        # sa.false(): booleano portável (DEFAULT 0 é rejeitado pelo PostgreSQL).
        sa.Column('enviado', sa.Boolean(), server_default=sa.false(), nullable=False),
        sa.Column('criado_em', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['empresa_id'], ['empresas.id'], name='fk_emails_enviados_empresa'),
        sa.PrimaryKeyConstraint('id'),
    )
    with op.batch_alter_table('emails_enviados', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_emails_enviados_empresa_id'), ['empresa_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_emails_enviados_criado_em'), ['criado_em'], unique=False)


def downgrade():
    with op.batch_alter_table('emails_enviados', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_emails_enviados_criado_em'))
        batch_op.drop_index(batch_op.f('ix_emails_enviados_empresa_id'))
    op.drop_table('emails_enviados')
