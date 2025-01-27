"""Add userRequestTable

Revision ID: 6d73e91951b2
Revises: 175881f5de4d
Create Date: 2025-01-21 23:38:05.868328

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy import Boolean, BigInteger, DateTime, Enum, func
import enum

# revision identifiers, used by Alembic.
revision: str = '6d73e91951b2'
down_revision: Union[str, None] = '175881f5de4d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade():
    # Create the table using the existing ENUM type (don't try to create it again)
    op.create_table(
        'user_request_tables',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('practice_id', sa.BigInteger(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=True, default=True),
        sa.Column('role', postgresql.ENUM('admin', 'practice_user', name='userroletype', create_type = False), nullable=False, default='practice_user'),
        sa.Column('status', sa.Boolean(), nullable=False, default=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.ForeignKeyConstraint(['practice_id'], ['practices.id']),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade():
    # Drop the table if you need to revert the migration
    op.drop_table('user_request_tables')
