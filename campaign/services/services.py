from centralised_models import UserCampaign, CampaignStatus
from utils import db_manager
from ..serializers import UserCampaignSerializer
from sqlalchemy.orm.exc import NoResultFound


class CampaignService:
    @staticmethod
    def create_campaign(validated_data, user):
        campaign_type = "Default" if user.is_super_admin else "Custom"
        with db_manager.get_db() as db_session:
            campaign = UserCampaign(
                title=validated_data['title'],
                description=validated_data.get('description'),
                status=CampaignStatus.SCHEDULED.value,
                created_by=user.id,
                type = campaign_type,
            )
            db_session.add(campaign)
            db_session.commit()
            return UserCampaignSerializer(campaign).data

    @staticmethod
    def list_campaigns():
        with db_manager.get_db() as db_session:
            # Query campaigns where type is "Default"
            campaigns = db_session.query(UserCampaign).filter(
                UserCampaign.type == "Default"
            ).all()

            return UserCampaignSerializer(campaigns, many=True).data

    @staticmethod
    def list_admin_campaigns(user):
        with db_manager.get_db() as db_session:
            # Query campaigns where created_by is user.id and type is "Custom"
            campaigns = db_session.query(UserCampaign).filter(
                UserCampaign.created_by == user.id,
                UserCampaign.type == "Custom"
            ).all()

            return UserCampaignSerializer(campaigns, many=True).data

    @staticmethod
    def retrieve_campaign(campaign_id):
        with db_manager.get_db() as db_session:
            campaign = db_session.query(UserCampaign).filter(UserCampaign.id == campaign_id).first()
            if not campaign:
                raise NoResultFound("Campaign not found")
            return UserCampaignSerializer(campaign).data

    @staticmethod
    def update_campaign(campaign_id, updated_data, user):
        with db_manager.get_db() as db_session:
            campaign = db_session.query(UserCampaign).filter(UserCampaign.id == campaign_id).first()

            if not campaign:
                raise NoResultFound("Campaign not found")

            # Check if the logged-in user is the creator of the campaign
            if campaign.created_by != user.id:
                raise PermissionError("You do not have permission to update this campaign")

            # Update the campaign fields
            for key, value in updated_data.items():
                if hasattr(campaign, key):
                    setattr(campaign, key, value)

            db_session.commit()
            return UserCampaignSerializer(campaign).data

    @staticmethod
    def delete_campaign(campaign_id, user):
        with db_manager.get_db() as db_session:
            # Query the campaign
            campaign = db_session.query(UserCampaign).filter(UserCampaign.id == campaign_id).first()

            # If the campaign is not found, raise an error
            if not campaign:
                raise NoResultFound("Campaign not found")

            # Check if the logged-in user is the creator of the campaign
            if campaign.created_by != user.id:
                raise PermissionError("You do not have permission to delete this campaign")

            # Delete the campaign
            db_session.delete(campaign)

            # Commit the transaction to permanently delete the campaign
            db_session.commit()
