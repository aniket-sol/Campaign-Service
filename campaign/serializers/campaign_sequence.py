from rest_framework import serializers
from centralised_models import UserCampaignSequence, CampaignStatus

class UserCampaignSequenceSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    user_campaign_id = serializers.IntegerField()
    scheduled_date = serializers.DateTimeField(required=True)
    # schedule_time = serializers.TimeField(allow_null=True, required=False)  # New field
    status = serializers.ChoiceField(choices=[status.value for status in CampaignStatus], required=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    # created_by = serializers.IntegerField()

    def create(self, validated_data):
        """
        Create and return a new `UserCampaignSequence` instance.
        """
        return UserCampaignSequence(**validated_data)

    def update(self, instance, validated_data):
        """
        Update and return an existing `UserCampaignSequence` instance.
        """
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        return instance
