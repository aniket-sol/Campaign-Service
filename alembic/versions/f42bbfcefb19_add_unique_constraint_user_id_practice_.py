"""Add_unique_constraint_user_id_practice_id_rolesTable

Revision ID: f42bbfcefb19
Revises: 52f30e225f1f
Create Date: 2025-01-22 16:53:34.223792

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f42bbfcefb19'
down_revision: Union[str, None] = '52f30e225f1f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
        Add a unique index on user_id and practice_id in the PracticeUserRole table
        """
    op.create_unique_constraint(
        'uq_user_practice',  # Name of the unique constraint
        'practice_user_roles',  # Table name
        ['user_id', 'practice_id']  # Columns to include in the unique constraint
    )


def downgrade() -> None:
    op.drop_constraint(
        'uq_user_practice',  # Name of the unique constraint
        'practice_user_roles',  # Table name
        type_='unique'  # Constraint type
    )
