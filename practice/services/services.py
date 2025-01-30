from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from users.models import PracticeUserRole
from utils import db_manager
from centralised_models import Practice

class PracticeService:
    """
    Service class to handle the business logic related to the `Practice` model.
    """
    @staticmethod
    def create_practice(data):
        """
        Update an existing message with new content, status, or sent_at.
        """
        try:
            with db_manager.get_db() as db_session:
                practice = Practice(
                    name=data['name'],
                    is_active=data.get('is_active', True)
                )
                db_session.add(practice)
                db_session.commit()
                db_session.refresh(practice)
                return {"id": practice.id}, None  # Return the created practice and no error
        except IntegrityError as e:
            print("Integrity error",str(e))
            return None, f"Integrity Error: {str(e)}"
        except Exception as e:
            print("Exception", str(e))
            return None, str(e)

    @staticmethod
    def get_practices():
        try:
            with db_manager.get_db() as db_session:
                practices = db_session.query(Practice).all()
                return practices, None  # Return the list of practices and no error
        except Exception as e:
            return None, str(e)

    @staticmethod
    def get_enrolled_practices(user):
        try:
            with db_manager.get_db() as db_session:
                # Query to join PracticeUserRole with Practice table
                practices = db_session.query(
                    PracticeUserRole.practice_id,
                    Practice.name.label('practice_name'),  # Assuming 'name' is the column in the 'Practice' table
                    PracticeUserRole.role
                ).join(
                    Practice, PracticeUserRole.practice_id == Practice.id
                    # Join condition between PracticeUserRole and Practice
                ).filter(
                    PracticeUserRole.user_id == user.id  # Filter by user_id
                ).all()

                practices = [
                    {
                        'practice_id': practice.practice_id,
                        'practice_name': practice.practice_name,
                        'role': practice.role.name  # Get the string representation of the Enum value
                    }
                    for practice in practices
                ]

                # Return list of practices (id, name) and None as error
                return practices, None
        except Exception as e:
            return None, str(e)

    @staticmethod
    def get_practice_by_id(practice_id):
        try:
            with db_manager.get_db() as db_session:
                practice = db_session.query(Practice).filter(Practice.id == practice_id).first()
                if not practice:
                    return None, "Practice not found"
                return practice, None  # Return the practice object and no error
        except Exception as e:
            return None, str(e)

    @staticmethod
    def update_practice(practice_id, data):
        try:
            with db_manager.get_db() as db_session:
                practice = db_session.query(Practice).filter(Practice.id == practice_id).first()

                if not practice:
                    return None, "Practice not found"

                # Update the practice fields
                practice.name = data.get('name', practice.name)
                practice.is_active = data.get('is_active', practice.is_active)
                db_session.commit()
                return practice, None  # Return the updated practice and no error
        except Exception as e:
            return None, str(e)

    @staticmethod
    def soft_delete_practice(practice_id):
        try:
            with db_manager.get_db() as db_session:
                practice = db_session.query(Practice).filter(Practice.id == practice_id).first()

                if not practice:
                    return None, "Practice not found"

                # Perform soft delete by setting is_active to False
                practice.is_active = False
                db_session.commit()
                return practice, None  # Return the practice after soft delete and no error
        except Exception as e:
            return None, str(e)