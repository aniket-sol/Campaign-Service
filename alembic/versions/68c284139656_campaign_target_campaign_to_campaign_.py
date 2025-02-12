"""campaign_target_campaign_to_campaign_sequence

Revision ID: 68c284139656
Revises: a4498670fa5f
Create Date: 2025-01-30 12:02:21.193064

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '68c284139656'
down_revision: Union[str, None] = 'a4498670fa5f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Drop the existing campaign_id column
    op.drop_constraint('campaign_target_campaign_id_fkey', 'campaign_target', type_='foreignkey')
    op.drop_column('campaign_target', 'campaign_id')

    # Add new campaign_sequence_id column with ON DELETE CASCADE
    op.add_column('campaign_target', sa.Column('campaign_sequence_id', sa.BigInteger(), nullable=False))
    op.create_foreign_key(
        'campaign_target_campaign_sequence_id_fkey',
        'campaign_target',
        'user_campaign_sequences',
        ['campaign_sequence_id'],
        ['id'],
        ondelete="CASCADE"
    )

def downgrade():
    # Reverse changes
    op.drop_constraint('campaign_target_campaign_sequence_id_fkey', 'campaign_target', type_='foreignkey')
    op.drop_column('campaign_target', 'campaign_sequence_id')

    # Re-add campaign_id column
    op.add_column('campaign_target', sa.Column('campaign_id', sa.BigInteger(), nullable=False))
    op.create_foreign_key(
        'campaign_target_campaign_id_fkey',
        'campaign_target',
        'user_campaigns',
        ['campaign_id'],
        ['id'],
        ondelete="CASCADE"
    )
