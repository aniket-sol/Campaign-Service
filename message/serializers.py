from rest_framework import serializers
from centralised_models import Message
from users.models import User
from centralised_models import UserCampaign
from datetime import datetime

class MessageSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    recipient_id = serializers.IntegerField(write_only=True)  # ForeignKey to User (UserID)
    content = serializers.CharField(max_length=2000)  # Message content
    status = serializers.ChoiceField(choices=['UNREAD', 'READ', 'SENT'])  # Message status

    def create(self, validated_data):
        """
        Create and return a new `Message` instance.
        """
        return Message(**validated_data)

    def update(self, instance, validated_data):
        """
        Update and return an existing `Message` instance.
        """
        return Message(**validated_data)
