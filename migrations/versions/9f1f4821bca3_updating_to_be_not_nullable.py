"""Updating to be not nullable

Revision ID: 9f1f4821bca3
Revises: ec85648a1114
Create Date: 2022-05-12 21:34:39.330610

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '9f1f4821bca3'
down_revision = 'ec85648a1114'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('session', 'valid',
               existing_type=sa.BOOLEAN(),
               nullable=False)
    op.alter_column('session', 'user_agent',
               existing_type=sa.VARCHAR(),
               nullable=False)
    op.alter_column('session', 'user_id',
               existing_type=postgresql.UUID(),
               nullable=False)
    op.alter_column('session', 'time_created',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               nullable=False)
    op.alter_column('session', 'time_updated',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               nullable=False)
    op.alter_column('user', 'email',
               existing_type=sa.VARCHAR(),
               nullable=False)
    op.alter_column('user', 'is_active',
               existing_type=sa.BOOLEAN(),
               nullable=False)
    op.alter_column('user', 'photo',
               existing_type=sa.VARCHAR(),
               nullable=False)
    op.alter_column('user', 'time_created',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               nullable=False)
    op.alter_column('user', 'time_updated',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               nullable=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('user', 'time_updated',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               nullable=True)
    op.alter_column('user', 'time_created',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               nullable=True)
    op.alter_column('user', 'photo',
               existing_type=sa.VARCHAR(),
               nullable=True)
    op.alter_column('user', 'is_active',
               existing_type=sa.BOOLEAN(),
               nullable=True)
    op.alter_column('user', 'email',
               existing_type=sa.VARCHAR(),
               nullable=True)
    op.alter_column('session', 'time_updated',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               nullable=True)
    op.alter_column('session', 'time_created',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               nullable=True)
    op.alter_column('session', 'user_id',
               existing_type=postgresql.UUID(),
               nullable=True)
    op.alter_column('session', 'user_agent',
               existing_type=sa.VARCHAR(),
               nullable=True)
    op.alter_column('session', 'valid',
               existing_type=sa.BOOLEAN(),
               nullable=True)
    # ### end Alembic commands ###