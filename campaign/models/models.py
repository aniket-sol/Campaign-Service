from sqlalchemy import Column, String, DateTime, ForeignKey, BigInteger,Text, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from users.models import UserRoleType
from utils import db_manager

Base = db_manager.Base


class CampaignStatus(enum.Enum):
    DRAFT = "DRAFT"
    SCHEDULED = "SCHEDULED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

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
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.current_timestamp())
    created_by = Column(BigInteger, ForeignKey('users.id'), nullable=False)

    #Relationships
    user = relationship("User", back_populates="created_campaigns")
    sequences = relationship("UserCampaignSequence", back_populates="user_campaign", cascade="all, delete")
    messages = relationship("Message", back_populates="campaign", cascade="all, delete")
    targets = relationship("CampaignTarget", back_populates="campaign", cascade="all, delete")

class UserCampaignSequence(Base):
    __tablename__ = 'user_campaign_sequences'

    id = Column(BigInteger, primary_key=True)
    user_campaign_id = Column(BigInteger, ForeignKey('user_campaigns.id'), nullable=False)
    scheduled_date = Column(DateTime(timezone=True), nullable=False)
    status = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.current_timestamp())
    created_by = Column(BigInteger, ForeignKey('users.id'), nullable=False)


    # Relationships
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

    # Relationships
    campaign = relationship("UserCampaign", back_populates="messages")
    recipient = relationship("User", back_populates="received_messages")


class CampaignTarget(Base):
    __tablename__ = 'campaign_target'

    id = Column(BigInteger, primary_key=True)
    campaign_id = Column(BigInteger, ForeignKey('user_campaigns.id'), nullable=False)
    practice_id = Column(BigInteger, ForeignKey('practices.id'), nullable=False)
    role = Column(SQLEnum(UserRoleType), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    campaign = relationship("UserCampaign", back_populates="targets")
    practice = relationship("Practice")
