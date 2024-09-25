from rest_framework import serializers
from .models import UserProgress


class UserProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProgress
        fields = [
            "video",
            "progress_percent",
            "last_accessed",
            "time_spent",
            "is_completed",
        ]
