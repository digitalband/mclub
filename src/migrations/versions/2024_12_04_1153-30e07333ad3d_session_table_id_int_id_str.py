"""session table id[int] -> id[str]

Revision ID: 30e07333ad3d
Revises: 640da571186b
Create Date: 2024-12-04 11:53:00.009265

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "30e07333ad3d"
down_revision: Union[str, None] = "640da571186b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column(
        "sessions",
        "id",
        existing_type=sa.INTEGER(),
        type_=sa.String(),
        existing_nullable=False,
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column(
        "sessions",
        "id",
        existing_type=sa.String(),
        type_=sa.INTEGER(),
        existing_nullable=False,
    )
    # ### end Alembic commands ###