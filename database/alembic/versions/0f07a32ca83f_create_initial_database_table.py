"""create initial database table

Revision ID: 0f07a32ca83f
Revises: 
Create Date: 2023-07-18 14:36:22.549220

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0f07a32ca83f'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'tourtrackerusers',
        sa.Column('id', sa.Integer, primary_key=True, index=True),
        sa.Column('email', sa.String(100), unique=True, index=True),
        sa.Column('username', sa.String(50), unique=True, index=True),
        sa.Column('password_hash', sa.String(100)),
        sa.Column('verified', sa.Boolean, default=False)
    )
    op.create_table(
        'arcadeusers',
        sa.Column('id', sa.Integer, primary_key=True, index=True),
        sa.Column('email', sa.String(100), unique=True, index=True),
        sa.Column('username', sa.String(50), unique=True, index=True),
        sa.Column('password_hash', sa.String(100)),
        sa.Column('verified', sa.Boolean, default=False)
    )


def downgrade() -> None:
    op.drop_table('tourtrackerusers')
    op.drop_table('arcadeusers')
