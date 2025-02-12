from celery_config import app
from utils import db_manager
from centralised_models import UserCampaign
from message.services import MessageService

@app.task
def send_campaign_messages(practice_ids, roles, user_campaign_id, campaign_data, campaign_sequence_id):
    """
    Celery task to send messages when the scheduled date is reached.
    """
    try:
        with db_manager.get_db() as db_session:
            user_campaign = db_session.query(UserCampaign).filter(UserCampaign.id == user_campaign_id).first()

            if user_campaign:
                MessageService.send_messages(practice_ids, roles, user_campaign_id, campaign_data, campaign_sequence_id)
            else:
                print("User campaign not found.")
    except Exception as e:
        print(f"Error sending messages: {e}")
