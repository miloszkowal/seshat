"""empty message

Revision ID: eea59e5ab42f
Revises: dd4fdb8191c0
Create Date: 2019-11-05 17:56:23.128974

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'eea59e5ab42f'
down_revision = 'dd4fdb8191c0'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    # op.drop_column('book', 'cover_image')
    # ### end Alembic commands ###
    pass


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('book', sa.Column('cover_image', sa.VARCHAR(length=20), nullable=False))
    # ### end Alembic commands ###
