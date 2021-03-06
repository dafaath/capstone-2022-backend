"""Updating user tabel

Revision ID: 012af9d23652
Revises: 29a7bb38b7a5
Create Date: 2022-05-12 19:53:02.849172

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '012af9d23652'
down_revision = '29a7bb38b7a5'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('session', 'is_active')
    op.add_column('user', sa.Column('photo', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'photo')
    op.add_column('session', sa.Column('is_active', sa.BOOLEAN(), autoincrement=False, nullable=True))
    # ### end Alembic commands ###
