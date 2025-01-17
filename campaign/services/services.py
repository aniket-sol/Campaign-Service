from centralised_models import UserCampaign, CampaignStatus
from utils import db_manager
from ..serializers import UserCampaignSerializer
from sqlalchemy.orm.exc import NoResultFound


class CampaignService:
    @staticmethod
    def create_campaign(validated_data, user):
        with db_manager.get_db() as db_session:
            campaign = UserCampaign(
                title=validated_data['title'],
                description=validated_data.get('description'),
                status=CampaignStatus.DRAFT.value,
                created_by=user.id
            )
            db_session.add(campaign)
            db_session.commit()
            return UserCampaignSerializer(campaign).data

    @staticmethod
    def list_campaigns():
        with db_manager.get_db() as db_session:
            campaigns = db_session.query(UserCampaign).all()
            return UserCampaignSerializer(campaigns, many=True).data

    @staticmethod
    def retrieve_campaign(campaign_id):
        with db_manager.get_db() as db_session:
            campaign = db_session.query(UserCampaign).filter(UserCampaign.id == campaign_id).first()
            if not campaign:
                raise NoResultFound("Campaign not found")
            return UserCampaignSerializer(campaign).data

    @staticmethod
    def update_campaign(campaign_id, updated_data):
        with db_manager.get_db() as db_session:
            campaign = db_session.query(UserCampaign).filter(UserCampaign.id == campaign_id).first()
            if not campaign:
                raise NoResultFound("Campaign not found")

            for key, value in updated_data.items():
                if hasattr(campaign, key):
                    setattr(campaign, key, value)
            db_session.commit()
            return UserCampaignSerializer(campaign).data

    @staticmethod
    def delete_campaign(campaign_id):
        with db_manager.get_db() as db_session:
            campaign = db_session.query(UserCampaign).filter(UserCampaign.id == campaign_id).first()
            if not campaign:
                raise NoResultFound("Campaign not found")
            campaign.is_active = False
            db_session.commit()
