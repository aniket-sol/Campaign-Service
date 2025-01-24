from sqlalchemy import false
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from users.models import UserRequestTable, UserRoleType, PracticeUserRole, User, Practice


class UserRequestService:
    @staticmethod
    def create_entry(data: dict, db_session: Session, user_id: int) -> UserRequestTable:
        """
        Create a new entry in the UserRequestTable.

        Parameters:
            data (dict): Data to create a new entry.
            db_session (Session): SQLAlchemy database session.

        Returns:
            UserRequestTable: The created UserRequestTable object.
            :param user_id:
        """
        new_entry = UserRequestTable(
            user_id=user_id,
            practice_id=data["practice_id"],
            role=data["role"],
            # is_active=data.get("is_active", True),
            # status=data.get("status", False)
        )
        db_session.add(new_entry)
        db_session.commit()
        db_session.refresh(new_entry)
        return new_entry

    @staticmethod
    def get_active_entries(db_session: Session) -> list:
        """
        Get a list of all entries where is_active is True.

        Parameters:
            db_session (Session): SQLAlchemy database session.

        Returns:
            list: A list of UserRequestTable entries where is_active is True.
        """
        # active_entries = db_session.query(UserRequestTable).filter(UserRequestTable.is_active == True).all()
        active_entries = (
            db_session.query(
                UserRequestTable,
                User.first_name,
                User.last_name,
                Practice.name.label("practice_name"),
            )
            .join(User, UserRequestTable.user_id == User.id)
            .join(Practice, UserRequestTable.practice_id == Practice.id)
            .filter(UserRequestTable.is_active == True)
            .all()
        )
        serialized_data = [
            {
                "id": entry.UserRequestTable.id,
                "user_id": entry.UserRequestTable.user_id,
                "practice_id": entry.UserRequestTable.practice_id,
                "role": entry.UserRequestTable.role.value,
                "created_at": entry.UserRequestTable.created_at,
                "user_first_name": entry.first_name,
                "user_last_name": entry.last_name,
                "practice_name": entry.practice_name,
            }
            for entry in active_entries
        ]
        return serialized_data
        # return active_entries

    def get_active_entries_practice_wise(db_session: Session, pk: int) -> list:
        """
        Get a list of all entries where is_active is True.

        Parameters:
            db_session (Session): SQLAlchemy database session.

        Returns:
            list: A list of UserRequestTable entries where is_active is True.
        """
        # active_entries = db_session.query(UserRequestTable).filter(UserRequestTable.is_active == True).all()
        print("In get_active_entries_practice_wise")
        active_entries = (
            db_session.query(
                UserRequestTable,
                User.first_name,
                User.last_name,
                Practice.name.label("practice_name"),
            )
            .join(User, UserRequestTable.user_id == User.id)
            .join(Practice, UserRequestTable.practice_id == Practice.id)
            .filter(UserRequestTable.is_active == True, pk == Practice.id)
            .all()
        )
        serialized_data = [
            {
                "id": entry.UserRequestTable.id,
                "user_id": entry.UserRequestTable.user_id,
                "practice_id": entry.UserRequestTable.practice_id,
                "role": entry.UserRequestTable.role.value,
                "created_at": entry.UserRequestTable.created_at,
                "user_first_name": entry.first_name,
                "user_last_name": entry.last_name,
                "practice_name": entry.practice_name,
            }
            for entry in active_entries
        ]
        return serialized_data
        # return active_entries

    @staticmethod
    def update_status_and_active(
            entry_id: int,
            user_id: int,
            practice_id: int,
            status: bool,
            role: UserRoleType,
            db_session: Session
    ) -> UserRequestTable:
        """
        Update the status and is_active fields of a UserRequestTable entry,
        and if the status is True, add an entry to the PracticeUserRole table.
        Both updates will be committed in a single transaction.

        Parameters:
            user_id (int): ID of the user.
            practice_id (int): ID of the practice.
            status (bool): New status value.
            role (UserRoleType): Role to be added to PracticeUserRole when status is True.
            db_session (Session): SQLAlchemy database session.

        Returns:
            UserRequestTable: The updated UserRequestTable object.
            :param db_session:
            :param role:
            :param status:
            :param practice_id:
            :param user_id:
            :param entry_id:
        """

        with db_session.begin():  # Automatically commits or rolls back
            # Fetch the user request entry by primary key
            entry = db_session.query(UserRequestTable).filter(
                UserRequestTable.id == entry_id
            ).first()

            if not entry:
                raise ValueError("Entry not found for the given user and practice")

            # Update the fields
            entry.status = status
            entry.is_active = False  # Assuming is_active is set to False for updates

            # Explicitly flush to ensure the update is processed
            db_session.flush()

            if status:  # If status is True, add or update a PracticeUserRole entry
                try:
                    # Check if an entry already exists
                    existing_entry = db_session.query(PracticeUserRole).filter_by(
                        user_id=user_id,
                        practice_id=practice_id
                    ).first()

                    if existing_entry:
                        # Update the role if an entry exists
                        existing_entry.role = role
                    else:
                        # Create a new entry if none exists
                        new_practice_user_role = PracticeUserRole(
                            user_id=user_id,
                            practice_id=practice_id,
                            role=role
                        )
                        db_session.add(new_practice_user_role)

                    # Explicitly flush to validate integrity constraints immediately
                    db_session.flush()

                except IntegrityError as e:
                    # Handle unique constraint violation gracefully
                    db_session.rollback()  # Rollback the transaction to maintain consistency
                    print("IntegrityError:", str(e))
                    raise ValueError(
                        "Duplicate entry detected: An entry with the same user_id and practice_id already exists.")

            # Refresh the entry object to ensure it reflects the latest database state
            db_session.refresh(entry)
            return entry

    # @staticmethod
    # def update_status_and_active(user_id: int, practice_id: int, status: bool, role:UserRoleType, db_session: Session) -> UserRequestTable:
    #     """
    #     Update the status and is_active fields of a UserRequestTable entry.
    #
    #     Parameters:
    #         user_id (int): ID of the user.
    #         practice_id (int): ID of the practice.
    #         status (bool): New status value.
    #         is_active (bool): New is_active value.
    #         db_session (Session): SQLAlchemy database session.
    #
    #     Returns:
    #         UserRequestTable: The updated UserRequestTable object.
    #         :param role:
    #     """
    #     entry = db_session.query(UserRequestTable).filter(
    #         UserRequestTable.user_id == user_id,
    #         UserRequestTable.practice_id == practice_id
    #     ).first()
    #
    #     if not entry:
    #         raise ValueError("Entry not found for the given user and practice")
    #
    #     entry.status = status
    #     entry.is_active = false
    #     db_session.commit()
    #     db_session.refresh(entry)
    #     return entry
