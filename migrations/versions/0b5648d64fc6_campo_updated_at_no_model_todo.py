"""campo updated_at no model Todo

Revision ID: 0b5648d64fc6
Revises: a2e7bfd16726
Create Date: 2024-09-30 15:27:41.337760

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0b5648d64fc6'
down_revision: Union[str, None] = 'a2e7bfd16726'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('todos', sa.Column('updated_at', sa.DateTime(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('todos', 'updated_at')
    # ### end Alembic commands ###
