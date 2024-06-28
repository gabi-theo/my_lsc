from datetime import datetime
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.db.models import Max
from rest_framework import serializers

from app.models import (
    AbsentStudent,
    CourseSchedule,
    DaysOff,
    MakeUp,
    News,
    Room,
    School,
    Session,
    SessionPresence,
    Student,
    Trainer,
    TrainerFromSchool,
    TrainerSchedule,
    User,
)
from app.services.trainers import TrainerService


##################################################### AUTH SERIALIZERS
class SignInSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    username = serializers.CharField(write_only=True)
    token = serializers.HiddenField(default=None)
    schools = serializers.SerializerMethodField(read_only=True)
    role = serializers.SerializerMethodField(read_only=True)
    user_id = serializers.SerializerMethodField(read_only=True)
    student_ids = serializers.SerializerMethodField(read_only=True)
    trainer_id = serializers.SerializerMethodField(read_only=True)


    class Meta:
        model = User
        fields = [
            "username",
            "password",
            "token",
            "schools",
            "role",
            "user_id",
            "student_ids",
            "trainer_id",
        ]

    def validate(self, attrs: dict) -> dict:
        data = super().validate(attrs)
        username = attrs.get("username", None)
        password = attrs.get("password", None)

        if username is None:
            raise serializers.ValidationError(
                "A username is required to sign-in.")

        if password is None:
            raise serializers.ValidationError(
                "A password is required to sign-in.")

        user = authenticate(username=username, password=password)

        if user is None:
            raise serializers.ValidationError(
                "This combination of username and password is invalid."
            )

        if not user.is_active:
            raise serializers.ValidationError(
                "This user has been deactivated.")

        data.update({"is_reset_password_needed": user.is_reset_password_needed})
        return data

    def get_schools(self, obj):
        resp_list = []
        schools = []
        # role: admin (work in progress?)
        '''
        {
            "schools": [],
            "role": null,
            "user_id": "48037275-5764-4707-9488-81cb0e5d4e48",
            "student_ids": null,
            "trainer_id": null
        }
        '''
        
        if obj.role == "coordinator":
            schools = obj.user_school.all()
        elif obj.role == "student":
            parent = obj.parent_user
            try:
                schools = parent.school.all()
            except Exception as e:
                schools = [parent.school]
        elif obj.role == "trainer":
            trainer = obj.trainer_user
            schools = TrainerFromSchool.objects.filter(trainer=trainer).schools.all()

        for school in schools:
            resp_list.append({str(school.id): school.name})
    
        return resp_list
    
    def get_role(self, obj):
        return obj.role
    
    def get_user_id(self, obj):
        return obj.id
    
    def get_student_ids(self, obj):
        try:
            parent = obj.parent_user
            if parent:
                students = parent.children.all()
                return [f"{student.id}_{student.first_name}_{student.last_name}" for student in students]
        except Exception:
            return None

    def get_trainer_id(self, obj):
        try:
            trainer = obj.trainer_user
            if trainer:
                return trainer.id
        except Exception:
            return None

class ResetPasswordSerializer(serializers.Serializer):
    password = serializers.CharField()
    user = serializers.HiddenField(default=None)

    class Meta:
        fields = [
            "password",
            "user",
        ]

    def validate(self, attrs: dict) -> dict:
        attrs = super().validate(attrs)
        request = self.context["request"]

        user = request.user
        validate_password(attrs["password"])

        attrs["user"] = user

        return attrs


############################################ SCHOOL SERIALIZER
class DaysOffSerializer(serializers.ModelSerializer):
    class Meta:
        model = DaysOff
        fields = ["first_day_off", "last_day_off", "day_off_info"]


class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ['id', 'room_name', 'capacity']


class SchoolSetupSerializer(serializers.ModelSerializer):

    user = serializers.CharField(read_only=True)

    class Meta:
        model = School
        fields = [
            "name",
            "phone_contact",
            "email_contact",
            "user",
        ]


######################################################### STUDENTS SERIALIZERS
class AbsencesSerializer(serializers.ModelSerializer):
    absent_participant_first_name = serializers.CharField(source="absent_participant.first_name")
    absent_participant_last_name = serializers.CharField(source="absent_participant.last_name")
    absent_participant_phone_number1 = serializers.CharField(source="absent_participant.parent.phone_number1")
    absent_participant_phone_number2 = serializers.CharField(source="absent_participant.parent.phone_number2")
    absent_on_session = serializers.CharField(source="absent_on_session.course_session.group_name")
    session_number = serializers.CharField(source="absent_on_session.session_no", read_only=True)
    student_school = serializers.SerializerMethodField(read_only=True)
    session_for_absence = serializers.SerializerMethodField(read_only=True)
    make_up_session_for_absence = serializers.SerializerMethodField(read_only=True)
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


########################################################## COURSES AND SESSIONS SERIALIZERS
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


class SessionPresenceSerializer(serializers.ModelSerializer):
    session = SessionListSerializer(read_only=True)
    class Meta:
        model = SessionPresence
        fields = '__all__'


########################################################## TRAINERS SERIALIZERS
class TrainerCreateUpdateSerializer(serializers.ModelSerializer):
    id = serializers.CharField(read_only=True)

    class Meta:
        model = Trainer
        fields = [
            "id",
            "first_name",
            "last_name",
            "phone_contact",
            "email_contact",
        ]

    def create(self, validated_data):
        validated_data["user"] = TrainerService.create_user_for_trainer_and_send_emai(
            username=f'{self.validated_data["first_name"]}.{self.validated_data["last_name"]}',
            trainer_email=self.validated_data["email_contact"]
        )
        print(validated_data["user"])
        trainer = Trainer.objects.create(
            user = validated_data["user"],
            first_name=self.validated_data["first_name"],
            last_name=self.validated_data["last_name"],
            phone_contact=self.validated_data["phone_contact"],
            email_contact=self.validated_data["email_contact"],
        )
        TrainerFromSchool.objects.create(
            trainer=trainer,
            # TODO: fix this for multiple schools
            school=self.context['request'].user.user_school.all().first(),
        )
        return trainer


class TrainerFromSchoolSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source="trainer.first_name")
    last_name = serializers.CharField(source="trainer.last_name")
    phone_contact = serializers.CharField(source="trainer.phone_contact")
    email_contact = serializers.CharField(source="trainer.email_contact")

    class Meta:
        model = TrainerFromSchool
        fields = ['trainer', 'first_name', 'last_name', 'phone_contact', 'email_contact']


class TrainerScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainerSchedule
        fields = '__all__'


######################################################### OTHER SERIALIZERS
class ImportSerializer(serializers.Serializer):
    file = serializers.FileField()


class NewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = News
        fields = "__all__"
