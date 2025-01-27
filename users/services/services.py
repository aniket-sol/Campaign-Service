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

    # def create_user_with_practice(self, validated_data: dict) -> User:
    #     """
    #     Handles user creation and practice-user role association.
    #     """
    #     username = validated_data["username"]
    #     email = validated_data["email"]
    #     password = validated_data["password"]
    #     first_name = validated_data.get("first_name")
    #     last_name = validated_data.get("last_name")
    #     practice_id = validated_data.get("practice_id")
    #
    #     # Validate practice_id if provided
    #     if practice_id:
    #         practice = self.db_session.query(Practice).filter_by(id=practice_id).first()
    #         if not practice:
    #             raise ValueError(f"Practice with ID {practice_id} does not exist.")
    #
    #     # Create the user
    #     user = self._create_user(
    #         username=username,
    #         email=email,
    #         password=password,
    #         first_name=first_name,
    #         last_name=last_name,
    #     )
    #
    #     # Associate user with practice if practice_id is provided
    #     if practice_id:
    #         self._associate_user_with_practice(user.id, practice_id)
    #
    #     return user


    # def _associate_user_with_practice(self, user_id: int, practice_id: int):
    #     """
    #     Associates a user with a practice in the PracticeUserRole table.
    #     """
    #     print('called')
    #     practice_user_role = PracticeUserRole(user_id=user_id, practice_id=practice_id)
    #     print(practice_user_role)
    #     try:
    #         self.db_session.add(practice_user_role)
    #         self.db_session.commit()
    #     except IntegrityError:
    #         self.db_session.rollback()
    #         raise ValueError("Failed to associate user with practice. Possibly a duplicate entry.")

