"""empty message

Revision ID: 6c399c69c57d
Revises: d7e29d85ad9c
Create Date: 2024-06-13 01:08:16.195933

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '6c399c69c57d'
down_revision = 'd7e29d85ad9c'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('users', 'last_name',
               existing_type=sa.VARCHAR(length=128),
               nullable=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('users', 'last_name',
               existing_type=sa.VARCHAR(length=128),
               nullable=False)
    # ### end Alembic commands ###