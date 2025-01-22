from sqlalchemy.orm import Session
from users.models import UserRequestTable

class UserRequestService:
    @staticmethod
    def create_entry(data: dict, db_session: Session) -> UserRequestTable:
        """
        Create a new entry in the UserRequestTable.

        Parameters:
            data (dict): Data to create a new entry.
            db_session (Session): SQLAlchemy database session.

        Returns:
            UserRequestTable: The created UserRequestTable object.
        """
        new_entry = UserRequestTable(
            user_id=data["user_id"],
            practice_id=data["practice_id"],
            role=data["role"],
            is_active=data.get("is_active", True),
            status=data.get("status", False)
        )
        db_session.add(new_entry)
        db_session.commit()
        db_session.refresh(new_entry)
        return new_entry

    @staticmethod
    def update_status_and_active(user_id: int, practice_id: int, status: bool, is_active: bool, db_session: Session) -> UserRequestTable:
        """
        Update the status and is_active fields of a UserRequestTable entry.

        Parameters:
            user_id (int): ID of the user.
            practice_id (int): ID of the practice.
            status (bool): New status value.
            is_active (bool): New is_active value.
            db_session (Session): SQLAlchemy database session.

        Returns:
            UserRequestTable: The updated UserRequestTable object.
        """
        entry = db_session.query(UserRequestTable).filter(
            UserRequestTable.user_id == user_id,
            UserRequestTable.practice_id == practice_id
        ).first()

        if not entry:
            raise ValueError("Entry not found for the given user and practice")

        entry.status = status
        entry.is_active = is_active
        db_session.commit()
        db_session.refresh(entry)
        return entry
