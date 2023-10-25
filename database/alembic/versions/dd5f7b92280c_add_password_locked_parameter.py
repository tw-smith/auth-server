"""add password_locked parameter

Revision ID: dd5f7b92280c
Revises: 0f07a32ca83f
Create Date: 2023-09-13 18:16:37.361307

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'dd5f7b92280c'
down_revision = '0f07a32ca83f'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('tourtrackerusers', sa.Column('password_locked', sa.Boolean, default=False))
    op.add_column('arcadeusers', sa.Column('password_locked', sa.Boolean, default=False))


def downgrade() -> None:
    op.drop_column('tourtrackerusers', 'password_locked')
    op.drop_column('arcadeusers', 'password_locked')
