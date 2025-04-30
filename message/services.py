from datetime import datetime
from sqlalchemy.orm import Session
from centralised_models import Message
from users.models import User
from centralised_models import UserCampaign
from .serializers import MessageSerializer


class MessageService:
    """
    Service class to handle the business logic related to the `Message` model.
    """
    @staticmethod
    def get_messages(db_session: Session, user_id: int):
        """
        Retrieve all messages whose `sent_at` is less than or equal to the current timestamp.

        Args:
            db_session (Session): SQLAlchemy session.

        Returns:
            List[Message]: List of messages with `sent_at` less than or equal to the current timestamp.
        """
        current_time = datetime.now()  # Get the current timestamp
        messages = db_session.query(Message).filter(Message.recipient_id == user_id, Message.sent_at <= current_time).all()

        if not messages:
            raise ValueError("No messages found with sent_at <= current timestamp")

        return messages



    @staticmethod
    def update_message(db_session: Session, message_id: int, user_id: int):
        """
        Update an existing message with new content, status, or sent_at.

        Args:
            db_session (Session): SQLAlchemy session.
            message_id (int): The ID of the message to update.

        Returns:
            Message: The updated message instance.
        """
        # Find the message to update
        message = db_session.query(Message).filter(Message.id == message_id).first()
        print(message)
        if not message:
            print("not found")
            raise ValueError("Message not found")

        if message.recipient_id == user_id:
            message.status = "READ"

        print(db_session.is_active)
        db_session.commit()
        return message

    # @staticmethod
    # def get_message(db_session: Session, message_id: int):
    #     """
    #     Retrieve a specific message by its ID.
    #
    #     Args:
    #         db_session (Session): SQLAlchemy session.
    #         message_id (int): The ID of the message to retrieve.
    #
    #     Returns:
    #         Message: The requested message.
    #     """
    #     message = db_session.query(Message).filter(Message.id == message_id).first()
    #
    #     if not message:
    #         raise ValueError("Message not found")
    #
    #     return message

    # @staticmethod
    # def get_messages_by_campaign(db_session: Session, campaign_id: int):
    #     """
    #     Retrieve all messages related to a specific campaign.
    #
    #     Args:
    #         db_session (Session): SQLAlchemy session.
    #         campaign_id (int): The ID of the campaign to fetch messages for.
    #
    #     Returns:
    #         List[Message]: List of messages related to the campaign.
    #     """
    #     messages = db_session.query(Message).filter(Message.campaign_id == campaign_id).all()
    #
    #     if not messages:
    #         raise ValueError("No messages found for this campaign")
    #
    #     return messages

    # @staticmethod
    # def create_message(db_session: Session, campaign_id: int, recipient_id: int, content: str, status: str = "UNREAD",
    #                    sent_at: datetime = None):
    #     """
    #     Create a new message and save it to the database.
    #
    #     Args:
    #         db_session (Session): SQLAlchemy session.
    #         campaign_id (int): The ID of the associated campaign.
    #         recipient_id (int): The ID of the recipient user.
    #         content (str): The content of the message.
    #         status (str): The status of the message (default: "UNREAD").
    #         sent_at (datetime, optional): The timestamp when the message was sent (default: None).
    #
    #     Returns:
    #         Message: The created message instance.
    #     """
    #     # Validate if campaign and recipient exist in the database
    #     campaign = db_session.query(UserCampaign).filter(UserCampaign.id == campaign_id).first()
    #     recipient = db_session.query(User).filter(User.id == recipient_id).first()
    #
    #     if not campaign:
    #         raise ValueError("Campaign not found")
    #     if not recipient:
    #         raise ValueError("Recipient not found")
    #
    #     # Create a new Message object
    #     new_message = Message(
    #         campaign_id=campaign_id,
    #         recipient_id=recipient_id,
    #         content=content,
    #         status=status,
    #         sent_at=sent_at,
    #         created_at=datetime.now(),
    #         updated_at=datetime.now()
    #     )
    #     db_session.add(new_message)
    #     db_session.commit()
    #
    #     return new_message
