from sqlalchemy import Column, Integer, String, DateTime, Boolean, Enum as SQLAEnum, ForeignKey, BigInteger
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func
from enum import Enum
from utils.db_manager import db_manager

Base = db_manager.Base


# SQLAlchemy Models
class UserRoleType(str, Enum):
    super_admin = "Practice by Numbers Support"
    admin = "Admin"
    practice_user = "Practice User"


class User(Base):
    __tablename__ = 'users'

    id = Column(BigInteger, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    username = Column(String, unique=True, nullable=False)
    first_name = Column(String)
    last_name = Column(String)
    is_active = Column(Boolean, default=True)
    is_staff = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)
    role = Column(SQLAEnum(UserRoleType), nullable=False, default=UserRoleType.practice_user)

    # Relationships
    practice_roles = relationship("PracticeUserRole", back_populates="user", cascade="all, delete")
    sessions = relationship("UserSession", back_populates="user", cascade="all, delete")
    created_campaigns = relationship("UserCampaign", back_populates="user", cascade="all, delete")
    created_sequences = relationship("UserCampaignSequence", back_populates="created_by_user", cascade="all, delete")
    received_messages = relationship("Message", back_populates="recipient", cascade="all, delete")

class Practice(Base):
    __tablename__ = 'practices'

    id = Column(BigInteger, primary_key=True)
    name = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    practice_users = relationship("PracticeUserRole", back_populates="practice")


class PracticeUserRole(Base):
    __tablename__ = 'practice_user_roles'

    id = Column(BigInteger, primary_key=True)
    user_id = Column(BigInteger, ForeignKey('users.id'), nullable=False)
    practice_id = Column(BigInteger, ForeignKey('practices.id'), nullable=False)

    # Relationships
    practice = relationship("Practice", back_populates="practice_users")
    user = relationship("User", back_populates="practice_roles")


class UserSession(Base):
    __tablename__ = 'user_sessions'

    id = Column(BigInteger, primary_key=True)
    user_id = Column(BigInteger, ForeignKey('users.id'), nullable=False)
    session_id = Column(String, unique=True, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True)

    # Relationships
    user = relationship("User", back_populates="sessions")

