"""implement on delete cascade

Revision ID: 087014829c7b
Revises: 5c11869faa38
Create Date: 2025-01-21 12:21:10.846177

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '087014829c7b'
down_revision: Union[str, None] = '5c11869faa38'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Modify foreign key constraints to include ON DELETE CASCADE

    # Update foreign key on practice_user_roles table
    op.drop_constraint('practice_user_roles_practice_id_fkey', 'practice_user_roles', type_='foreignkey')
    op.create_foreign_key('practice_user_roles_practice_id_fkey', 'practice_user_roles', 'practices', ['practice_id'],
                          ['id'], ondelete='CASCADE')

    op.drop_constraint('practice_user_roles_user_id_fkey', 'practice_user_roles', type_='foreignkey')
    op.create_foreign_key('practice_user_roles_user_id_fkey', 'practice_user_roles', 'users', ['user_id'], ['id'],
                          ondelete='CASCADE')

    # Update foreign key on user_campaigns table
    op.drop_constraint('user_campaigns_created_by_fkey', 'user_campaigns', type_='foreignkey')
    op.create_foreign_key('user_campaigns_created_by_fkey', 'user_campaigns', 'users', ['created_by'], ['id'],
                          ondelete='CASCADE')

    # Update foreign key on user_sessions table
    op.drop_constraint('user_sessions_user_id_fkey', 'user_sessions', type_='foreignkey')
    op.create_foreign_key('user_sessions_user_id_fkey', 'user_sessions', 'users', ['user_id'], ['id'],
                          ondelete='CASCADE')

    # Update foreign key on campaign_target table
    op.drop_constraint('campaign_target_campaign_id_fkey', 'campaign_target', type_='foreignkey')
    op.create_foreign_key('campaign_target_campaign_id_fkey', 'campaign_target', 'user_campaigns', ['campaign_id'],
                          ['id'], ondelete='CASCADE')

    op.drop_constraint('campaign_target_practice_id_fkey', 'campaign_target', type_='foreignkey')
    op.create_foreign_key('campaign_target_practice_id_fkey', 'campaign_target', 'practices', ['practice_id'], ['id'],
                          ondelete='CASCADE')

    # Update foreign key on message table
    op.drop_constraint('message_campaign_id_fkey', 'message', type_='foreignkey')
    op.create_foreign_key('message_campaign_id_fkey', 'message', 'user_campaigns', ['campaign_id'], ['id'],
                          ondelete='CASCADE')

    op.drop_constraint('message_recipient_id_fkey', 'message', type_='foreignkey')
    op.create_foreign_key('message_recipient_id_fkey', 'message', 'users', ['recipient_id'], ['id'], ondelete='CASCADE')

    # Update foreign key on user_campaign_sequences table
    op.drop_constraint('user_campaign_sequences_created_by_fkey', 'user_campaign_sequences', type_='foreignkey')
    op.create_foreign_key('user_campaign_sequences_created_by_fkey', 'user_campaign_sequences', 'users', ['created_by'],
                          ['id'], ondelete='CASCADE')

    op.drop_constraint('user_campaign_sequences_user_campaign_id_fkey', 'user_campaign_sequences', type_='foreignkey')
    op.create_foreign_key('user_campaign_sequences_user_campaign_id_fkey', 'user_campaign_sequences', 'user_campaigns',
                          ['user_campaign_id'], ['id'], ondelete='CASCADE')


def downgrade() -> None:
    # Remove ON DELETE CASCADE and revert to default behavior

    # Revert foreign key on practice_user_roles table
    op.drop_constraint('practice_user_roles_practice_id_fkey', 'practice_user_roles', type_='foreignkey')
    op.create_foreign_key('practice_user_roles_practice_id_fkey', 'practice_user_roles', 'practices', ['practice_id'],
                          ['id'])

    op.drop_constraint('practice_user_roles_user_id_fkey', 'practice_user_roles', type_='foreignkey')
    op.create_foreign_key('practice_user_roles_user_id_fkey', 'practice_user_roles', 'users', ['user_id'], ['id'])

    # Revert foreign key on user_campaigns table
    op.drop_constraint('user_campaigns_created_by_fkey', 'user_campaigns', type_='foreignkey')
    op.create_foreign_key('user_campaigns_created_by_fkey', 'user_campaigns', 'users', ['created_by'], ['id'])

    # Revert foreign key on user_sessions table
    op.drop_constraint('user_sessions_user_id_fkey', 'user_sessions', type_='foreignkey')
    op.create_foreign_key('user_sessions_user_id_fkey', 'user_sessions', 'users', ['user_id'], ['id'])

    # Revert foreign key on campaign_target table
    op.drop_constraint('campaign_target_campaign_id_fkey', 'campaign_target', type_='foreignkey')
    op.create_foreign_key('campaign_target_campaign_id_fkey', 'campaign_target', 'user_campaigns', ['campaign_id'],
                          ['id'])

    op.drop_constraint('campaign_target_practice_id_fkey', 'campaign_target', type_='foreignkey')
    op.create_foreign_key('campaign_target_practice_id_fkey', 'campaign_target', 'practices', ['practice_id'], ['id'])

    # Revert foreign key on message table
    op.drop_constraint('message_campaign_id_fkey', 'message', type_='foreignkey')
    op.create_foreign_key('message_campaign_id_fkey', 'message', 'user_campaigns', ['campaign_id'], ['id'])

    op.drop_constraint('message_recipient_id_fkey', 'message', type_='foreignkey')
    op.create_foreign_key('message_recipient_id_fkey', 'message', 'users', ['recipient_id'], ['id'])

    # Revert foreign key on user_campaign_sequences table
    op.drop_constraint('user_campaign_sequences_created_by_fkey', 'user_campaign_sequences', type_='foreignkey')
    op.create_foreign_key('user_campaign_sequences_created_by_fkey', 'user_campaign_sequences', 'users', ['created_by'],
                          ['id'])

    op.drop_constraint('user_campaign_sequences_user_campaign_id_fkey', 'user_campaign_sequences', type_='foreignkey')
    op.create_foreign_key('user_campaign_sequences_user_campaign_id_fkey', 'user_campaign_sequences', 'user_campaigns',
                          ['user_campaign_id'], ['id'])
