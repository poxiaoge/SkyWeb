"""add User.confirmed

Revision ID: 29d2bd0b51d5
Revises: 49f2d1c20971
Create Date: 2016-11-25 20:56:30.433175

"""

# revision identifiers, used by Alembic.
revision = '29d2bd0b51d5'
down_revision = '49f2d1c20971'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('confirmed', sa.BOOLEAN(), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'confirmed')
    ### end Alembic commands ###
