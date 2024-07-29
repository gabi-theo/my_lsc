from rest_framework import serializers

from app.models import Feedback


class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = [
            "feedback_for",
            "recipient",
            "content",
        ]