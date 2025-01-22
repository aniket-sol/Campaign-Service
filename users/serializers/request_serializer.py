from rest_framework import serializers
from users.models import UserRoleType

class UserRequestCreateSerializer(serializers.Serializer):
    """
    Serializer for creating a new user request entry.
    """
    user_id = serializers.IntegerField(required=True)
    practice_id = serializers.IntegerField(required=True)
    role = serializers.ChoiceField(choices=[role.value for role in UserRoleType], required=True)
    is_active = serializers.BooleanField(default=True)
    status = serializers.BooleanField(default=False)


class UserRequestUpdateSerializer(serializers.Serializer):
    """
    Serializer for updating the status and is_active fields.
    """
    user_id = serializers.IntegerField(required=True)
    practice_id = serializers.IntegerField(required=True)
    status = serializers.BooleanField(required=True)
    is_active = serializers.BooleanField(required=True)
