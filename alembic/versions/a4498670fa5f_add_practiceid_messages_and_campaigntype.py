"""add_practiceId_messages_and_campaignType

Revision ID: a4498670fa5f
Revises: f42bbfcefb19
Create Date: 2025-01-28 11:45:35.651581

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import enum
from sqlalchemy.dialects.postgresql import ENUM


# Define the enum for user_campaigns.type
class CampaignTypeEnum(enum.Enum):
    Default = "Default"
    Custom = "Custom"

# revision identifiers, used by Alembic.
revision: str = 'a4498670fa5f'
down_revision: Union[str, None] = 'f42bbfcefb19'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Step 1: Create the 'campaign_type' enum type in PostgreSQL
    campaign_type_enum = sa.Enum(CampaignTypeEnum, name='campaign_type')
    campaign_type_enum.create(op.get_bind(), checkfirst=True)

    # Step 2: Add 'practice_id' column to the 'message' table
    op.add_column('message', sa.Column('practice_id', sa.BigInteger(), nullable=False, server_default='2'))

    # Step 3: Create a foreign key relationship from 'practice_id' to 'practices' table
    op.create_foreign_key('fk_message_practice', 'message', 'practices', ['practice_id'], ['id'])

    # Step 4: Add 'type' column to the 'user_campaigns' table with the 'campaign_type' enum type
    op.add_column('user_campaigns', sa.Column('type', campaign_type_enum, nullable=False, server_default='Default'))


def downgrade() -> None:
    # Step 1: Drop the foreign key relationship for 'practice_id' from 'message' table
    op.drop_constraint('fk_message_practice', 'message', type_='foreignkey')

    # Step 2: Remove 'practice_id' column from the 'message' table
    op.drop_column('message', 'practice_id')

    # Step 3: Remove 'type' column from the 'user_campaigns' table
    op.drop_column('user_campaigns', 'type')

    # Step 4: Drop the 'campaign_type' enum type from PostgreSQL
    sa.Enum(CampaignTypeEnum, name='campaign_type').drop(op.get_bind(), checkfirst=True)
