"""Add schedule_time and update status to Enum in usersequenceStatus

Revision ID: 175881f5de4d
Revises: 087014829c7b
Create Date: 2025-01-21 15:31:17.807704

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ENUM


# revision identifiers, used by Alembic.
revision: str = '175881f5de4d'
down_revision: Union[str, None] = '087014829c7b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

campaign_status_enum = ENUM('DRAFT', 'SENT', 'SCHEDULED', name='campaignstatus', create_type=False)

def upgrade() -> None:
    # Create the enum type for CampaignStatus if not exists
    campaign_status_enum.create(op.get_bind(), checkfirst=True)

    # Drop the existing 'status' column
    op.drop_column('user_campaign_sequences', 'status')

    # Add the 'status' column again with the ENUM type
    op.add_column('user_campaign_sequences',
                  sa.Column('status', campaign_status_enum, nullable=False, server_default='DRAFT'))

def downgrade() -> None:
    # Drop the 'status' column
    op.drop_column('user_campaign_sequences', 'status')

    # Add the 'status' column again as VARCHAR
    op.add_column('user_campaign_sequences',
                  sa.Column('status', sa.String(), nullable=False, server_default='DRAFT'))

    # Drop the enum type for CampaignStatus
    campaign_status_enum.drop(op.get_bind(), checkfirst=True)
