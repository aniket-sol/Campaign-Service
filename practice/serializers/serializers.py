from rest_framework import serializers
from users.models import Practice  # Import your SQLAlchemy Practice model

class PracticeSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=255)
    is_active = serializers.BooleanField(default=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    def create(self, validated_data):
        db_session = self.context.get('db_session')  # Pass the session via context
        practice = Practice(**validated_data)
        db_session.add(practice)
        db_session.commit()
        db_session.refresh(practice)
        return practice

    def update(self, instance, validated_data):
        db_session = self.context.get('db_session')  # Pass the session via context
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        db_session.commit()
        db_session.refresh(instance)
        return instance
