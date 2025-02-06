"""fixing campaign_sequences_status_enum

Revision ID: 09a00ebb897b
Revises: 68c284139656
Create Date: 2025-02-06 11:14:13.520601

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from enum import Enum
from sqlalchemy import Enum as SQLEnum


# revision identifiers, used by Alembic.
revision: str = '09a00ebb897b'
down_revision: Union[str, None] = '68c284139656'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


class NewCampaignStatus(Enum):
    SCHEDULED = "SCHEDULED"
    SENT = "SENT"


def upgrade():
    # Drop existing column and add new one
    with op.batch_alter_table('user_campaign_sequences') as batch_op:
        batch_op.drop_column('status')

        batch_op.add_column(
            sa.Column(
                'status',
                SQLEnum(NewCampaignStatus, name='campaignstatus'),
                nullable=False,
                server_default=NewCampaignStatus.SCHEDULED.value
            )
        )


def downgrade():
    with op.batch_alter_table('user_campaign_sequences') as batch_op:
        batch_op.drop_column('status')