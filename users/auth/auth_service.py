from datetime import datetime, timedelta
from passlib.context import CryptContext
from rest_framework.exceptions import AuthenticationFailed, PermissionDenied
import uuid
from users.models import User, UserSession
from utils import db_manager
import pytz

# Password hashing utility
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
now_aware = datetime.now(pytz.utc)

class AuthService:
    """
    Handles authentication, session management, and authorization tasks.
    """

    @staticmethod
    def authenticate_user(email: str, password: str) -> dict[str, str | datetime]:
        """
        Authenticates a user by their email and password, and creates a session.

        Args:
            email (str): User's email.
            password (str): User's password.

        Returns:
            dict: The session data containing user_id, session_token, and expires_at.
        """
        with db_manager.get_db() as db_session:
            # Query user by email
            user = db_session.query(User).filter(User.email == email).first()
            if user is None or not pwd_context.verify(password, user.password):
                raise AuthenticationFailed("Invalid email or password")

            # Create a new session
            session_token = str(uuid.uuid4())
            expires_at = datetime.now() + timedelta(days=2)  # Session expiration set to 2 days
            user_session = UserSession(
                user_id=user.id,
                session_id=session_token,
                expires_at=expires_at,
                is_active=True
            )
            db_session.add(user_session)
            db_session.commit()

            return {
                "user_id": user.id,
                "session_token": session_token,
                "expires_at": expires_at
            }

    @staticmethod
    def validate_session(session_token: str) -> User:
        """
        Validates a session token and retrieves the associated user.

        Args:
            session_token (str): The session token.

        Returns:
            User: The authenticated user.

        Raises:
            AuthenticationFailed: If the token is invalid or expired.
        """
        # print(session_token)
        with db_manager.get_db() as db_session:
            user_session = db_session.query(UserSession).filter(
                UserSession.session_id == session_token,
                UserSession.is_active == True
            ).first()

            if not user_session or user_session.expires_at < now_aware:
                raise AuthenticationFailed("Session token is invalid or expired")

            # Fetch the associated user
            user = db_session.query(User).filter(User.id == user_session.user_id).first()
            if not user:
                raise AuthenticationFailed("User not found for the session")

            return user

    @staticmethod
    def invalidate_session(session_token: str) -> None:
        """
        Invalidates a session token by deactivating it.

        Args:
            session_token (str): The session token.

        Raises:
            AuthenticationFailed: If the token is invalid.
        """
        with db_manager.get_db() as db_session:
            user_session = db_session.query(UserSession).filter(
                UserSession.session_id == session_token
            ).first()

            if not user_session:
                raise AuthenticationFailed("Invalid session token")

            user_session.is_active = False
            db_session.commit()

    @staticmethod
    def is_authorized(user_id: int, allowed_roles: list) -> None:
        # Retrieve the user from the database
        with db_manager.get_db() as db_session:
            user = db_session.query(User).filter(User.id == user_id).first()

            if not user:
                raise PermissionDenied("User not found")

            if user.role.value not in allowed_roles:
                # print("User is not authorized")
                raise PermissionDenied("You do not have permission to perform this action")
