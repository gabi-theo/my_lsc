from rest_framework import serializers

from app.models import (
    AbsentStudent,
    Student,
)


class AbsencesSerializer(serializers.ModelSerializer):
    absent_participant_first_name = serializers.CharField(
        source="absent_participant.first_name")
    absent_participant_last_name = serializers.CharField(
        source="absent_participant.last_name")
    absent_participant_phone_number1 = serializers.CharField(
        source="absent_participant.parent.phone_number1")
    absent_participant_phone_number2 = serializers.CharField(
        source="absent_participant.parent.phone_number2")
    absent_on_session = serializers.CharField(
        source="absent_on_session.course_session.group_name")
    session_number = serializers.CharField(
        source="absent_on_session.session_no", read_only=True)
    student_school = serializers.SerializerMethodField(read_only=True)
    session_for_absence = serializers.SerializerMethodField(read_only=True)
    make_up_session_for_absence = serializers.SerializerMethodField(
        read_only=True)
    school_for_absence = serializers.SerializerMethodField(read_only=True)
    make_up_date_and_time = serializers.SerializerMethodField(read_only=True)
    trainer = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = AbsentStudent
        fields = [
            "id",
            "absent_participant_first_name",
            "absent_participant_last_name",
            "absent_participant_phone_number1",
            "absent_participant_phone_number2",
            "absent_on_session",
            "is_absence_in_crm",
            "is_absence_communicated_to_parent",
            "has_make_up_scheduled",
            "is_absence_completed",
            "is_absent_for_absence",
            "comment",
            "session_number",
            "session_for_absence",
            "make_up_session_for_absence",
            "school_for_absence",
            "student_school",
            "make_up_date_and_time",
            "trainer",
        ]

    def get_student_school(self, obj):
        return obj.absent_on_session.course_session.school.name

    def get_trainer(self, obj):
        if obj.has_make_up_scheduled:
            try:
                if obj.choosed_make_up_session_for_absence:
                    return obj.choosed_make_up_session_for_absence.trainer.__str__()
                return obj.choosed_course_session_for_absence.session_trainer.__str__()
            except:
                pass
        return None

    def get_make_up_date_and_time(self, obj):
        if obj.has_make_up_scheduled:
            try:
                if obj.choosed_make_up_session_for_absence:
                    return obj.choosed_make_up_session_for_absence.date_time
                return f"{obj.choosed_course_session_for_absence.date} - {obj.choosed_course_session_for_absence.course_session.start_time}"
            except:
                pass
        return None

    def get_make_up_session_for_absence(self, obj):
        if obj.choosed_make_up_session_for_absence:
            return obj.choosed_make_up_session_for_absence.date_time
        return None

    def get_session_for_absence(self, obj):
        if obj.choosed_course_session_for_absence:
            return obj.choosed_course_session_for_absence.course_session.group_name
        return None

    def get_school_for_absence(self, obj):
        if obj.choosed_make_up_session_for_absence:
            return obj.absent_on_session.course_session.school.name
        elif obj.choosed_course_session_for_absence:
            return obj.choosed_course_session_for_absence.course_session.school.name
        return None


class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = "__all__"


class StudentsEmailSerializer(serializers.Serializer):
    groups = serializers.CharField()
    subject = serializers.CharField()
    message = serializers.CharField(style={'base_template': 'textarea.html'})
    send_mail = serializers.BooleanField(default=False)
    send_whatsapp = serializers.BooleanField(default=False)

    class Meta:
        fields = [
            "groups",
            "subject",
            "message",
            "send_mail",
            "send_whatsapp",
        ]
