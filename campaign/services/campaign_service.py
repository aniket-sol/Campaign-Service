from centralised_models import UserCampaignSequence, CampaignStatus, UserCampaign, CampaignTarget, PracticeUserRole, Message
from utils import db_manager
from ..serializers import UserCampaignSequenceSerializer
from sqlalchemy.orm.exc import NoResultFound


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
            db_session.flush()  # Ensure the ID is generated before using it

            # Create CampaignTarget entries
            target_data = []
            for practice_id in practice_ids:
                for role in roles:
                    target_data.append({
                        'user_sequence_id': campaign_sequence.id,  # Changed from user_campaign_id
                        'practice_id': practice_id,
                        'role': role
                    })

            # print("target_data", target_data)

            # Insert the CampaignTarget entries
            CampaignSequenceService.create_campaign_targets(db_session, target_data)

            # print("campaign_sequence", campaign_sequence)
            if user_campaign.type == "Custom":
                user_campaign.status = "SENT"

            db_session.commit()

            # Send messages to relevant users
            CampaignSequenceService.send_messages(db_session, practice_ids, roles, user_campaign, user_campaign_id,
                                                  user, campaign_data)

            # Return the serialized campaign sequence data
            return UserCampaignSequenceSerializer(campaign_sequence).data

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
    def send_messages(db_session, practice_ids, roles, user_campaign, user_sequence_id, user, campaign_data):
        """
        Sends messages to users based on the practice_ids and roles.

        Args:
            db_session (Session): The SQLAlchemy session.
            practice_ids (list): List of practice IDs to filter users.
            roles (list): List of roles to filter users.
            user_sequence_id (int): The ID of the campaign sequence.
            user (User): The user who is initiating the message creation (typically the creator of the campaign).
            campaign_data (dict): Additional data related to the campaign.

        Returns:
            None
        """
        try:
            # Find all user IDs from the PracticeUserRole table for the given practice_ids and roles
            users_to_notify = db_session.query(PracticeUserRole.user_id).filter(
                PracticeUserRole.practice_id.in_(practice_ids),
                PracticeUserRole.role.in_(roles)
            ).all()

            # If no users are found, return early
            if not users_to_notify:
                return

            # Iterate through the users and create messages for each one
            for user_id in users_to_notify:
                # Create a message for each user
                message = Message(
                    campaign_sequence_id=user_sequence_id,  # Changed from campaign_id
                    recipient_id=user_id[0],  # user_id is returned as a tuple (user_id,)
                    content=user_campaign.description,  # Reference to the campaign description
                    status='UNREAD',  # Default status for a new message
                    sent_at=campaign_data['scheduled_date'],
                )
                db_session.add(message)

            db_session.commit()  # Commit after adding all messages

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
