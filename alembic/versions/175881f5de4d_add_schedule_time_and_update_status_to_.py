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

    # Add the new column 'schedule_time'
    op.add_column('user_campaign_sequences', sa.Column('schedule_time', sa.DateTime(timezone=True), nullable=True))

    # Modify 'status' column to use ENUM
    op.execute(
        "ALTER TABLE user_campaign_sequences ALTER COLUMN status TYPE campaignstatus USING status::campaignstatus"
    )

def downgrade() -> None:
    # Revert 'status' column back to String with a USING clause
    op.execute(
        "ALTER TABLE user_campaign_sequences ALTER COLUMN status TYPE VARCHAR USING status::TEXT"
    )

    # Remove the 'schedule_time' column
    op.drop_column('user_campaign_sequences', 'schedule_time')

    # Drop the enum type for CampaignStatus
    campaign_status_enum.drop(op.get_bind(), checkfirst=True)
