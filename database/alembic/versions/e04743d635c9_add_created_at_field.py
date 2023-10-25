"""add created_at field

Revision ID: e04743d635c9
Revises: dd5f7b92280c
Create Date: 2023-09-13 21:15:53.585245

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e04743d635c9'
down_revision = 'dd5f7b92280c'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('tourtrackerusers', sa.Column('created_at', sa.Integer))
    op.add_column('arcadeusers', sa.Column('created_at', sa.Integer))


def downgrade() -> None:
    op.drop_column('tourtrackerusers', 'created_at')
    op.drop_column('arcadeusers', 'created_at')