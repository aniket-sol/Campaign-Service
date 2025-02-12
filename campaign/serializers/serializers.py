from rest_framework import serializers
from centralised_models import UserCampaign

class UserCampaignSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    title = serializers.CharField(max_length=255)
    description = serializers.CharField(allow_blank=True, required=False)
    status = serializers.CharField(max_length=255)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    # created_by = serializers.IntegerField()

    def create(self, validated_data):
        """
        Create and return a new `UserCampaign` instance.
        """
        return UserCampaign(**validated_data)

    def update(self, instance, validated_data):
        """
        Update and return an existing `UserCampaign` instance.
        """
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        return instance
