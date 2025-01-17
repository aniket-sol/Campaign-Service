from rest_framework import serializers
from ..models import UserCampaign


class UserCampaignSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserCampaign
        fields = ('id', 'title', 'description', 'status', 'created_by', 'created_at', 'updated_at')
