from datetime import datetime
from centralised_models import UserCampaignSequence, CampaignStatus, UserCampaign, CampaignTarget
from ..serializers import UserCampaignSequenceSerializer
from sqlalchemy.orm.exc import NoResultFound
from utils import db_manager
from tasks import send_campaign_messages

class CampaignSequenceService:
    @staticmethod
    def create_campaign_with_targets(user_campaign_id, practice_ids, roles, campaign_data, user):
        """
        Creates a campaign sequence and campaign targets for the given user_campaign_id,
        practice_ids, and roles.

        Args:
            user_campaign_id (int): The ID of the user campaign.
            practice_ids (list): List of practice IDs to associate with the campaign targets.
            roles (list): List of roles to associate with the campaign targets.
            campaign_data (dict): Additional campaign data (e.g., scheduled_date).
            user (User): The user making the request.

        Returns:
            dict: Serialized data of the created campaign sequence.
        """
        try:
            with db_manager.get_db() as db_session:
                # Ensure that the UserCampaign exists
                user_campaign = db_session.query(UserCampaign).filter(UserCampaign.id == user_campaign_id).first()
                if not user_campaign:
                    raise NoResultFound("User campaign not found.")

                # Create a new campaign sequence entry
                campaign_sequence = UserCampaignSequence(
                    user_campaign_id=user_campaign_id,
                    scheduled_date=campaign_data['scheduled_date'],
                    status='SCHEDULED',  # Default status, could be passed from request if needed
                    created_by=user.id
                )
                db_session.add(campaign_sequence)

                # Ensure the ID of campaign_sequence is generated and available
                db_session.flush()

                # Create CampaignTarget entries
                target_data = []
                for practice_id in practice_ids:
                    for role in roles:
                        target_data.append({
                            'user_sequence_id': campaign_sequence.id,  # Changed from user_campaign_id
                            'practice_id': practice_id,
                            'role': role
                        })

                # Insert the CampaignTarget entries
                CampaignSequenceService.create_campaign_targets(db_session, target_data)

                # Commit all changes to the session (this is where the changes are saved to the DB)
                db_session.commit()

                # Calculate the time delay based on scheduled_date
                scheduled_datetime = campaign_data['scheduled_date']
                scheduled_datetime = datetime.strptime(campaign_data['scheduled_date'], "%Y-%m-%dT%H:%M")
                current_time = datetime.now()

                # If the scheduled time is in the future, schedule the message sending task
                if scheduled_datetime > current_time:
                    delay = (scheduled_datetime - current_time).total_seconds()
                    send_campaign_messages.apply_async(
                        args=[practice_ids, roles, user_campaign_id, campaign_data],
                        countdown=delay  # Set delay until the scheduled time
                    )
                else:
                    # If the scheduled time is in the past, send immediately
                    send_campaign_messages.apply_async(
                        args=[practice_ids, roles, user_campaign_id, campaign_data]
                    )
                # Send messages to relevant users
                # MessageService.send_messages(practice_ids, roles, user_campaign.id, campaign_data)

                # Return the serialized campaign sequence data
                return UserCampaignSequenceSerializer(campaign_sequence).data

        except Exception as e:
            # In case of any exception, we handle it and rollback if necessary
            db_session.rollback()  # Rollback the session to avoid partial commit
            print(f"Error occurred while creating campaign sequence and targets: {str(e)}")
            # You can customize this message or error handling logic
            return {'error': str(e)}

    @staticmethod
    def create_campaign_targets(db_session, target_data):
        """
        Helper method to insert multiple CampaignTarget entries into the database.

        Args:
            db_session (Session): The SQLAlchemy session.
            target_data (list): List of dictionaries containing campaign target data.

        Returns:
            None
        """
        try:
            for data in target_data:
                campaign_target = CampaignTarget(
                    campaign_sequence_id=data['user_sequence_id'],  # Changed from user_campaign_id
                    practice_id=data['practice_id'],
                    role=data['role']
                )
                db_session.add(campaign_target)

            db_session.commit()  # Commit the transaction after adding all targets
        except Exception as e:
            db_session.rollback()  # Rollback in case of error
            raise e  # Re-raise the error for further handling


    @staticmethod
    def create_campaign_sequence(validated_data, user):
        """
        Create a new campaign sequence.
        """
        # print(validated_data)
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
