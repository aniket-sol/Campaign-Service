from centralised_models import UserCampaignSequence, CampaignStatus
from utils import db_manager
from ..serializers import UserCampaignSequenceSerializer
from sqlalchemy.orm.exc import NoResultFound


class CampaignSequenceService:
    @staticmethod
    def create_campaign_sequence(validated_data, user):
        """
        Create a new campaign sequence.
        """
        print(validated_data)
        with db_manager.get_db() as db_session:
            campaign_sequence = UserCampaignSequence(
                user_campaign_id=validated_data['user_campaign_id'],
                scheduled_date=validated_data['scheduled_date'],
                # schedule_time=validated_data.get('schedule_time'),
                status=CampaignStatus.DRAFT.value,
                created_by=user.id
            )
            db_session.add(campaign_sequence)
            db_session.commit()
            return UserCampaignSequenceSerializer(campaign_sequence).data

    @staticmethod
    def list_campaign_sequences():
        """
        List all campaign sequences.
        """
        with db_manager.get_db() as db_session:
            campaign_sequences = db_session.query(UserCampaignSequence).all()
            return UserCampaignSequenceSerializer(campaign_sequences, many=True).data

    @staticmethod
    def retrieve_campaign_sequence(sequence_id):
        """
        Retrieve a single campaign sequence by ID.
        """
        with db_manager.get_db() as db_session:
            campaign_sequence = (
                db_session.query(UserCampaignSequence)
                .filter(UserCampaignSequence.id == sequence_id)
                .first()
            )
            if not campaign_sequence:
                raise NoResultFound("Campaign sequence not found")
            return UserCampaignSequenceSerializer(campaign_sequence).data

    @staticmethod
    def update_campaign_sequence(sequence_id, updated_data):
        """
        Update a campaign sequence.
        """
        with db_manager.get_db() as db_session:
            campaign_sequence = (
                db_session.query(UserCampaignSequence)
                .filter(UserCampaignSequence.id == sequence_id)
                .first()
            )
            if not campaign_sequence:
                raise NoResultFound("Campaign sequence not found")

            for key, value in updated_data.items():
                if hasattr(campaign_sequence, key):
                    setattr(campaign_sequence, key, value)
            db_session.commit()
            return UserCampaignSequenceSerializer(campaign_sequence).data

    @staticmethod
    def delete_campaign_sequence(sequence_id):
        """
        Soft delete a campaign sequence.
        """
        with db_manager.get_db() as db_session:
            campaign_sequence = (
                db_session.query(UserCampaignSequence)
                .filter(UserCampaignSequence.id == sequence_id)
                .first()
            )
            if not campaign_sequence:
                raise NoResultFound("Campaign sequence not found")
            campaign_sequence.status = CampaignStatus.DELETED.value
            db_session.commit()
