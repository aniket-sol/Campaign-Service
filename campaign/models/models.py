from sqlalchemy import Column,Date, Time,  String, DateTime, ForeignKey, BigInteger,Text, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from users.models import UserRoleType
from utils import db_manager

Base = db_manager.Base


class CampaignStatus(enum.Enum):
    DRAFT = "DRAFT"
    SCHEDULED = "SCHEDULED"
    IN_PROGRESS = "SENT"

class MessageStatus(enum.Enum):
    # PENDING = "PENDING"
    UNREAD = "UNREAD"
    READ = "READ"
    DELETED = "DELETED"


class UserCampaign(Base):
    __tablename__ = 'user_campaigns'

    id = Column(BigInteger, primary_key=True)
    title = Column(String, nullable=False, unique=True)
    description = Column(String)
    status = Column(String, nullable=False)
    type = Column(SQLEnum("Default", "Custom", name="campaign_type"), nullable=False, default="Default")  # Added "type" field
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.current_timestamp())
    created_by = Column(BigInteger, ForeignKey('users.id'), nullable=False)

    #Relationships
    user = relationship("User", back_populates="created_campaigns")
    sequences = relationship("UserCampaignSequence", back_populates="user_campaign", cascade="all, delete")
    messages = relationship("Message", back_populates="campaign", cascade="all, delete")

class UserCampaignSequence(Base):
    __tablename__ = 'user_campaign_sequences'

    id = Column(BigInteger, primary_key=True)
    user_campaign_id = Column(BigInteger, ForeignKey('user_campaigns.id'), nullable=False)
    scheduled_date = Column(DateTime(timezone=True), nullable=False)
    status = Column(SQLEnum(CampaignStatus), nullable=False)  # Updated to use Enum
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.current_timestamp())
    created_by = Column(BigInteger, ForeignKey('users.id'), nullable=False)


    # Relationships
    targets = relationship("CampaignTarget", back_populates="campaign_sequence", cascade="all, delete")
    user_campaign = relationship("UserCampaign", back_populates="sequences")
    created_by_user = relationship("User", back_populates="created_sequences")

class Message(Base):
    __tablename__ = 'message'

    id = Column(BigInteger, primary_key=True)
    campaign_id = Column(BigInteger, ForeignKey('user_campaigns.id'), nullable=False)
    recipient_id = Column(BigInteger, ForeignKey('users.id'), nullable=False)
    content = Column(Text, nullable=False)  # Content dynamically references UserCampaign description
    status = Column(SQLEnum(MessageStatus), nullable=False, default=MessageStatus.UNREAD)
    sent_at = Column(DateTime(timezone=True))
    read_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.current_timestamp())
    # practice_id = Column(BigInteger, ForeignKey('practices.id'), nullable=False, default=2)  # Added practice_id reference

    # Relationships
    campaign = relationship("UserCampaign", back_populates="messages")
    recipient = relationship("User", back_populates="received_messages")
    # practice = relationship("Practice", back_populates="practices_messages")  # Added practice relationship

class CampaignTarget(Base):
    __tablename__ = 'campaign_target'

    id = Column(BigInteger, primary_key=True)
    campaign_sequence_id = Column(BigInteger, ForeignKey('user_campaign_sequences.id'), nullable=False)  # Updated
    practice_id = Column(BigInteger, ForeignKey('practices.id'), nullable=False)
    role = Column(SQLEnum(UserRoleType), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    campaign_sequence = relationship("UserCampaignSequence")  # Updated
    practice = relationship("Practice")
