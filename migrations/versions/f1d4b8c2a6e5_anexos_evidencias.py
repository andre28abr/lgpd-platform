"""anexos (evidencias) de RIPD, incidente e pedido do titular

Revision ID: f1d4b8c2a6e5
Revises: e9c3a7b5d2f1
Create Date: 2026-09-10 16:00:00.000000

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = 'f1d4b8c2a6e5'
down_revision = 'e9c3a7b5d2f1'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'anexos',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('empresa_id', sa.Integer(), nullable=False),
        sa.Column('alvo_tipo', sa.String(length=20), nullable=False),
        sa.Column('alvo_id', sa.Integer(), nullable=False),
        sa.Column('nome_original', sa.String(length=255), nullable=False),
        sa.Column('nome_arquivo', sa.String(length=80), nullable=False),
        sa.Column('mime', sa.String(length=100), nullable=True),
        sa.Column('tamanho', sa.Integer(), nullable=True),
        sa.Column('enviado_por_id', sa.Integer(), nullable=True),
        sa.Column('criado_em', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['empresa_id'], ['empresas.id'], name='fk_anexos_empresa'),
        sa.ForeignKeyConstraint(['enviado_por_id'], ['usuarios.id'], name='fk_anexos_usuario'),
        sa.PrimaryKeyConstraint('id'),
    )
    with op.batch_alter_table('anexos', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_anexos_empresa_id'), ['empresa_id'], unique=False)
        batch_op.create_index('ix_anexos_alvo', ['empresa_id', 'alvo_tipo', 'alvo_id'], unique=False)


def downgrade():
    with op.batch_alter_table('anexos', schema=None) as batch_op:
        batch_op.drop_index('ix_anexos_alvo')
        batch_op.drop_index(batch_op.f('ix_anexos_empresa_id'))
    op.drop_table('anexos')
