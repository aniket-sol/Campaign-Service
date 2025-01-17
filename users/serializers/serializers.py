from sqlalchemy.orm import Session
from ..models import User
from rest_framework import serializers

class UserCreateSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True)
    first_name = serializers.CharField(required=False, allow_blank=True)
    last_name = serializers.CharField(required=False, allow_blank=True)


    def __init__(self, *args, **kwargs):
        # Pass the SQLAlchemy session when initializing the serializer
        self.db_session: Session = kwargs.pop("db_session", None)
        super().__init__(*args, **kwargs)

    def validate_email(self, value):
        if not self.db_session:
            raise ValueError("Database session is required to validate email")

        # Query the database using SQLAlchemy to check if the email exists
        user_exists = self.db_session.query(User).filter(User.email == value).first()
        if user_exists:
            raise serializers.ValidationError("Email already registered")
        return value

    def validate_username(self, value):
        if not self.db_session:
            raise ValueError("Database session is required to validate username")

        # Query the database using SQLAlchemy to check if the email exists
        user_exists = self.db_session.query(User).filter(User.username == value).first()
        if user_exists:
            raise serializers.ValidationError("Username already registered")
        return value

class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
