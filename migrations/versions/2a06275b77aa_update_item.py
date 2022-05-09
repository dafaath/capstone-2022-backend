"""Update item

Revision ID: 2a06275b77aa
Revises: 1fdcb6b7e9a3
Create Date: 2022-05-08 22:57:27.156223

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2a06275b77aa'
down_revision = '1fdcb6b7e9a3'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('items', sa.Column('locus', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('items', 'locus')
    # ### end Alembic commands ###
