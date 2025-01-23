"""move_role_user_practiceuserrole_added_issuperadmin

Revision ID: 52f30e225f1f
Revises: 6d73e91951b2
Create Date: 2025-01-22 10:32:48.318570

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '52f30e225f1f'
down_revision: Union[str, None] = '6d73e91951b2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', sa.Column('is_super_admin', sa.Boolean(), nullable=False, server_default=sa.text('false')))

    # Drop role column from users table
    op.drop_column('users', 'role')

    # Add role column to practice_user_roles table
    # user_role_type_enum = postgresql.ENUM('practice_user', 'admin',
    #                                       name='userroletype')  # Adjust enum values as per your UserRoleType

    op.add_column('practice_user_roles',
                  sa.Column('role', postgresql.ENUM('practice_user', 'admin', name='userroletype', create_type=False), nullable=False,
                            server_default='practice_user'))


def downgrade() -> None:
    # Remove is_super_admin column from users table
    op.drop_column('users', 'is_super_admin')

    # Remove role column from practice_user_roles table
    op.drop_column('practice_user_roles', 'role')

    # Re-add role column to users table
    op.add_column('users', sa.Column('role', postgresql.ENUM('practice_user', 'admin', name='userroletype', create_type=False), nullable=False,
                            server_default='practice_user'))


