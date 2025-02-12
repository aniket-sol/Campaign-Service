from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from centralised_models import User, Practice, PracticeUserRole
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserService:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def create_user(self, validated_data: dict) -> User:
        """
        Creates and saves a new user in the database.
        """
        username = validated_data["username"]
        email = validated_data["email"]
        password = validated_data["password"]
        first_name = validated_data.get("first_name")
        last_name = validated_data.get("last_name")

        hashed_password = pwd_context.hash(password)

        user = User(
            username=username,
            email=email,
            password=hashed_password,
            first_name=first_name,
            last_name=last_name,
        )

        try:
            self.db_session.add(user)
            self.db_session.commit()
        except IntegrityError:
            self.db_session.rollback()
            raise ValueError("User with the given username or email already exists.")

        return user

    def change_password(self, user: User, current_password: str, new_password: str):
        user_in_db = self.db_session.query(User).filter(User.id == user.id).first()

        if not user_in_db:
            return {"error": "User not found"}

        if not pwd_context.verify(current_password, user_in_db.password):
            return {"error": "Current password is incorrect"}

        if len(new_password) < 6:
            return {"error": "New password must be at least 6 characters long"}

        # Update the password inside the session
        user_in_db.password = pwd_context.hash(new_password)

        self.db_session.commit()  # Commit changes to the database

        return {"message": "Password changed successfully"}




    def get_user_practice_role(self, user_id: int) -> dict:
        """
        Retrieve the user's role from the practice_user_roles table.

        Parameters:
            user_id (int): ID of the user.

        Returns:
            dict or None: The role of the user in the specified practice, or None if not found.
        """
        practice_role = self.db_session.query(PracticeUserRole).filter(
            PracticeUserRole.user_id == user_id,
        ).first()

        if practice_role:
            return {
                "role": practice_role.role.value,
                "practice_name": practice_role.practice.name,  # Assuming practice has a 'name' attribute
                "practice_id": practice_role.practice.id,  # Assuming practice has an 'id' attribute
            }
        return None

