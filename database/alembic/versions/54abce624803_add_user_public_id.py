"""add user public id

Revision ID: 54abce624803
Revises: e04743d635c9
Create Date: 2023-09-15 11:17:58.306012

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '54abce624803'
down_revision = 'e04743d635c9'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('tourtrackerusers', sa.Column('public_id', sa.String))
    op.add_column('arcadeusers', sa.Column('public_id', sa.String))


def downgrade() -> None:
    op.drop_column('tourtrackerusers', 'public_id')
    op.drop_column('arcadeusers', 'public_id')