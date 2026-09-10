"""leitura de trilhas (progresso do treinamento)

Revision ID: b3f7e1c9d5a2
Revises: a2e6c9d1f4b7
Create Date: 2026-09-10 20:00:00.000000

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = 'b3f7e1c9d5a2'
down_revision = 'a2e6c9d1f4b7'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'trilha_leituras',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('usuario_id', sa.Integer(), nullable=False),
        sa.Column('trilha_id', sa.Integer(), nullable=False),
        sa.Column('lido_em', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['usuario_id'], ['usuarios.id'], name='fk_trilha_leituras_usuario'),
        sa.ForeignKeyConstraint(['trilha_id'], ['trilhas.id'], name='fk_trilha_leituras_trilha'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('usuario_id', 'trilha_id', name='uq_trilha_leitura'),
    )
    with op.batch_alter_table('trilha_leituras', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_trilha_leituras_usuario_id'), ['usuario_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_trilha_leituras_trilha_id'), ['trilha_id'], unique=False)


def downgrade():
    with op.batch_alter_table('trilha_leituras', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_trilha_leituras_trilha_id'))
        batch_op.drop_index(batch_op.f('ix_trilha_leituras_usuario_id'))
    op.drop_table('trilha_leituras')
