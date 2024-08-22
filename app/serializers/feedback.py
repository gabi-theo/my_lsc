from rest_framework import serializers

from app.models import (Feedback, School, Student, User)


class FeedbackSerializer(serializers.ModelSerializer):

    id = serializers.UUIDField(read_only=True)
    role_of_submiter = serializers.CharField()

    submission_date = serializers.DateField(read_only=True)

    submited_by = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        required=False, allow_null=True
    )
    submited_for_student = serializers.PrimaryKeyRelatedField(
        queryset=Student.objects.all(),
        required=False, allow_null=True
    )
    feedback_for_school = serializers.PrimaryKeyRelatedField(
        queryset=School.objects.all(),
        required=False, allow_null=True
    )

    class Meta:
        model = Feedback
        fields = [
            "id",
            "role_of_submiter",
            "feedback_for",
            "recipient",
            "content",
            "submission_date",
            "submited_by",
            "submited_for_student",
            "feedback_for_school",
            "is_anonymised",
        ]
