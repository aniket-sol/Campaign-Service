from rest_framework import serializers
from sqlalchemy.orm import Session
from ..models import UserRequestTable, User, Practice, UserRoleType


class UserRequestTableCreateSerializer(serializers.Serializer):
    user_id = serializers.IntegerField(required=True)
    practice_id = serializers.IntegerField(required=True)
    is_active = serializers.BooleanField(default=True)
    role = serializers.ChoiceField(choices=[role.value for role in UserRoleType],
                                   default=UserRoleType.practice_user)
    status = serializers.BooleanField(default=False)

    # Read-only fields that are auto-generated
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    def __init__(self, *args, **kwargs):
        """
        Pass the SQLAlchemy session when initializing the serializer.
        """
        self.db_session: Session = kwargs.pop("db_session", None)
        super().__init__(*args, **kwargs)

    def validate_user_id(self, value):
        """
        Validate that the user_id exists in the database.
        """
        if not self.db_session:
            raise ValueError("Database session is required to validate user_id")

        user = self.db_session.query(User).filter_by(id=value).first()
        if not user:
            raise serializers.ValidationError(f"User with ID {value} does not exist.")
        return value

    def validate_practice_id(self, value):
        """
        Validate that the practice_id exists in the database.
        """
        if not self.db_session:
            raise ValueError("Database session is required to validate practice_id")

        practice = self.db_session.query(Practice).filter_by(id=value).first()
        if not practice:
            raise serializers.ValidationError(f"Practice with ID {value} does not exist.")
        return value

    def create(self, validated_data):
        """
        Create a new UserRequestTable instance using the validated data.
        """
        if not self.db_session:
            raise ValueError("Database session is required to create a new record")

        # Create the new UserRequestTable instance and save to DB
        user_request = UserRequestTable(**validated_data)
        self.db_session.add(user_request)
        self.db_session.commit()
        return user_request
