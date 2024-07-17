from datetime import datetime

from django.db.models import Max
from rest_framework import serializers

from app.models import CourseSchedule

from .students import StudentSerializer


class CourseScheduleSerializer(serializers.ModelSerializer):
    students = StudentSerializer(read_only=True, many=True)
    course = serializers.CharField(read_only=True, source="course.course_type")
    default_trainer_first_name = serializers.CharField(read_only=True, source="default_trainer.first_name")
    default_trainer_last_name = serializers.CharField(read_only=True, source="default_trainer.last_name")
    current_session = serializers.SerializerMethodField()

    class Meta:
        model = CourseSchedule
        fields = [
            "id",
            "available_places_for_make_up_online",
            "available_places_for_make_up_on_site",
            "can_be_used_as_online_make_up_for_other_schools",
            "classroom",
            "course",
            "course_type",
            "day",
            "default_trainer",
            "classroom",
            "default_trainer_first_name",
            "default_trainer_last_name",
            "first_day_of_session",
            "group_name",
            "id",
            "last_day_of_session",
            "online_link",
            "school",
            "students",
            "start_time",
            "total_sessions",
            "current_session",
        ]

    def get_current_session(self, obj):
        today = datetime.now().date()
        current_week_sessions = obj.sessions.filter(date__week=today.isocalendar()[1])

        if current_week_sessions.exists():
            current_session = current_week_sessions.first()
        else:
            latest_session = obj.sessions.aggregate(Max('date'))['date__max']
            if latest_session:
                current_session = obj.sessions.filter(date=latest_session).first()
            else:
                current_session = None

        if current_session:
            return current_session.session_no
        else:
            return None