"""empty message

Revision ID: 2b6f6e5b1b8f
Revises: b0319c006d92
Create Date: 2019-11-12 17:17:54.480246

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2b6f6e5b1b8f'
down_revision = 'b0319c006d92'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('first_name', sa.String(length=50), nullable=True))
    op.add_column('user', sa.Column('last_name', sa.String(length=50), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'last_name')
    op.drop_column('user', 'first_name')
    # ### end Alembic commands ###
