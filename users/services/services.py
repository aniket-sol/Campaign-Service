# users/services.py
from passlib.context import CryptContext
from ..models import User
from sqlalchemy.orm import Session

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserService:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def create_user(self, username: str, email: str, password: str, first_name: str = None, last_name: str = None) -> User:
        # Hash the password
        hashed_password = pwd_context.hash(password)

        # Create the user instance using SQLAlchemy
        user = User(
            username=username,
            email=email,
            password=hashed_password,
            first_name=first_name,
            last_name=last_name
        )

        # Add the new user to the session and commit using SQLAlchemy
        # Add the user to the session
        self.db_session.add(user)

        # Commit the transaction to save the user
        self.db_session.commit()

        # Return the created user
        return user
