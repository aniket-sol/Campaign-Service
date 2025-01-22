from rest_framework import serializers
from users.models import UserRoleType

class UserRequestTableSerializer(serializers.Serializer):
    """
    Serializer for creating a new user request entry.
    """
    id = serializers.IntegerField(read_only=True)
    user_id = serializers.IntegerField(required=True)
    practice_id = serializers.IntegerField(required=True)
    role = serializers.ChoiceField(choices=[role.value for role in UserRoleType], required=True)
    created_at = serializers.DateTimeField(read_only=True)

class UserRequestCreateSerializer(serializers.Serializer):
    """
    Serializer for creating a new user request entry.
    """
    practice_id = serializers.IntegerField(required=True)
    role = serializers.ChoiceField(
        choices=[role.value for role in UserRoleType],
        required=False,  # Mark as optional
    )
    is_active = serializers.BooleanField(default=True)  # Default value is True
    status = serializers.BooleanField(default=False)  # Default value is False

    def validate(self, attrs):
        # Set default role if not provided
        if 'role' not in attrs or not attrs['role']:
            attrs['role'] = UserRoleType.practice_user.value  # Replace DEFAULT with the desired default role
        return attrs


class UserRequestUpdateSerializer(serializers.Serializer):
    """
    Serializer for updating the status and is_active fields.
    """
    user_id = serializers.IntegerField(required=True)
    practice_id = serializers.IntegerField(required=True)
    status = serializers.BooleanField(required=True)
    role = serializers.ChoiceField(choices=[role.value for role in UserRoleType], required=True)
    # is_active = serializers.BooleanField(required=True)
