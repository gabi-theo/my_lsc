from rest_framework import serializers

from app.models import (
    MakeUp,
    Session,
    SessionPresence,
)


class MakeUpSerializer(serializers.ModelSerializer):
    make_up_for_session = serializers.CharField(source="make_up_for_session.course_session.course.course_type")
    make_up_for_session_number = serializers.CharField(source="make_up_for_session.session_no")
    make_up_time = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = MakeUp
        fields = '__all__'

    def get_make_up_time(self, obj):
        return f"{obj.make_up_on.hour}:{obj.make_up_on.minute}"


class SessionSerializer(serializers.ModelSerializer):
    course_session_id = serializers.CharField(source="course_session.id")
    course_session = serializers.CharField(source="course_session.group_name")
    no_of_students = serializers.SerializerMethodField(read_only=True)
    no_of_absences = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Session
        fields = ['id', 'course_session_id', 'course_session', 'session_passed', 'date',
                  'session_no', 'course_session', 'no_of_absences', 'no_of_students']

    def get_no_of_students(self, obj):
        return obj.course_session.students.all().count()
    
    def get_no_of_absences(self, obj):
        return obj.course_session_absence.all().count()


class SessionListSerializer(serializers.ModelSerializer):
    time = serializers.SerializerMethodField(read_only=True)
    course_session = serializers.CharField(source="course_session.course.course_type", read_only=True)
    session_trainer = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Session
        fields = [
            "id",
            "course_session",
            "session_no",
            "session_trainer",
            "date",
            "time",
        ]

    def get_time(self, obj):
        return obj.course_session.start_time

    def get_session_trainer(self, obj):
        return obj.session_trainer.__str__()


class SessionForCalendarSerializer(SessionSerializer):
    class Meta:
        model = Session
        fields = ['id', 'course_session_id', 'course_session', 'session_passed', 'date', 'session_no']

class SessionPresenceSerializer(serializers.ModelSerializer):
    session = SessionListSerializer(read_only=True)
    class Meta:
        model = SessionPresence
        fields = '__all__'