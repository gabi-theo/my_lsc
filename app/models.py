import uuid
from datetime import datetime, timedelta

from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    """
    User model manager where username is the unique identifiers
    for authentication instead of usernames.
    """

    def create_user(self, username, password, **extra_fields):
        """
        Create and save a User with the given username and password.
        """
        if not username:
            raise ValueError(_("The username must be set"))

        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save()

        return user

    def create_superuser(self, username, password, **extra_fields):
        """
        Create and save a SuperUser with the given username and password.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must have is_staff=True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser=True."))

        return self.create_user(username, password, **extra_fields)


class User(AbstractBaseUser):
    ROLE_CHOICES = (
        ("trainer", "Trainer"),
        ("student", "Student"),
        ("coordinator", "Coordinator"),
    )
    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = []

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    username = models.CharField(max_length=50, unique=True)
    is_superuser = models.BooleanField(
        _("superuser status"),
        default=False,
        help_text=_(
            "Designates that this user has all permissions without "
            "explicitly assigning them."
        ),
    )
    is_staff = models.BooleanField(
        _("staff status"),
        default=False,
        help_text=_(
            "Designates whether the user can log into this admin site."),
    )
    is_active = models.BooleanField(
        _("active"),
        default=True,
        help_text=_(
            "Designates whether this user should be treated as active. "
            "Unselect this instead of deleting accounts."
        ),
    )
    is_reset_password_email_token_expired = models.BooleanField(default=True)
    is_reset_password_token_expired = models.BooleanField(default=True)
    role = models.CharField(max_length=20,
                            choices=ROLE_CHOICES, blank=True, null=True)
    is_reset_password_needed = models.BooleanField(default=False)
    objects = UserManager()

    def _str_(self):
        return self.get_username()

    def has_perm(self, perm, obj=None):
        return self.is_superuser

    def has_module_perms(self, app_label):
        return self.is_superuser


class School(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="user_school",
    )
    name = models.CharField(
        null=False,
        blank=False,
        max_length=50,
    )
    phone_contact = models.CharField(max_length=50)
    email_contact = models.EmailField()
    smartbill_api_key = models.CharField(null=True, blank=True, max_length=100)

    def __str__(self) -> str:
        return self.name


class Room(models.Model):
    room_name = models.CharField(max_length=50, null=False, blank=False, default="room name")
    capacity = models.SmallIntegerField()
    school = models.ForeignKey(School, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f"{self.school} - {self.room_name} - {self.capacity}"


class DaysOff(models.Model):
    first_day_off = models.DateField()
    last_day_off = models.DateField()
    day_off_info = models.CharField(max_length=200)
    school = models.ForeignKey(School, on_delete=models.CASCADE)


class CourseDays(models.Model):
    DAYS = (
        ("luni", "Luni"),
        ("marti", "Marti"),
        ("miercuri", "Miercuri"),
        ("joi", "Joi"),
        ("vineri", "Vineri"),
        ("sambata", "Sambata"),
        ("duminica", "Duminica"),
    )
    day = models.CharField(max_length=20, choices=DAYS)


class Course(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    next_possible_course = models.ManyToManyField(
        'self',
        blank=True,
        symmetrical=False,
        related_name='next_course'
    )
    course_type = models.CharField(max_length=50, null=False, blank=False)

    def __str__(self) -> str:
        return self.course_type


class Trainer(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, null=True, related_name="trainer_user")
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone_contact = models.CharField(max_length=50)
    email_contact = models.EmailField()

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}"


class TrainerFromSchool(models.Model):
    school = models.ForeignKey(School, on_delete=models.SET_NULL, null=True, blank=True, related_name="school_trainers")
    trainer = models.ForeignKey(Trainer, on_delete=models.CASCADE)

    # def __str__(self) -> str:
    #     return f"{self.trainer.__str__()} - {self.school.name}"

class Parent(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(
        School,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        related_name="school_students",
    )
    user = models.OneToOneField(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="parent_user")
    first_name = models.CharField(
        max_length=50, null=False, blank=False)
    last_name = models.CharField(
        max_length=50, null=False, blank=False)
    phone_number1 = models.CharField(
        max_length=50, null=True, blank=True)
    phone_number2 = models.CharField(
        max_length=50, null=True, blank=True)
    email1 = models.CharField(max_length=50, null=True, blank=True)
    email2 = models.CharField(max_length=50, null=True, blank=True)
    active_account = models.BooleanField(default=True)

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}"


class Student(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    parent = models.ForeignKey(Parent, on_delete=models.CASCADE, related_name="children")
    first_name = models.CharField(max_length=50, null=False, blank=False)
    last_name = models.CharField(max_length=50, null=False, blank=False)

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}"


class CourseSchedule(models.Model):
    DAYS = (
        ("luni", "Luni"),
        ("marti", "Marti"),
        ("miercuri", "Miercuri"),
        ("joi", "Joi"),
        ("vineri", "Vineri"),
        ("sambata", "Sambata"),
        ("duminica", "Duminica"),
    )

    TYPE = (
        ("onl", "Online"),
        ("hbr", "Hibrid"),
        ("sed", "Sediu"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name='course_schedules')
    school = models.ForeignKey(
        School,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        related_name="school_courses",
    )
    group_name = models.CharField(max_length=50, null=False, blank=False)
    total_sessions = models.SmallIntegerField()
    first_day_of_session = models.DateField(null=False, blank=False)
    last_day_of_session = models.DateField(null=False, blank=False)
    day = models.CharField(
        max_length=15,
        choices=DAYS,
    )
    start_time = models.TimeField(null=False)
    end_time = models.TimeField(default=None)
    classroom = models.ForeignKey(Room, models.SET_NULL, blank=True, null=True)
    default_trainer = models.ForeignKey(Trainer, on_delete=models.SET_NULL, null=True, blank=True)
    students = models.ManyToManyField(
        Student,
        related_name="course_schedule_students",
        through='StudentCourseSchedule',
    )
    course_type = models.CharField(max_length=10, choices=TYPE)
    online_link = models.CharField(max_length=500, null=True, blank=True)
    can_be_used_as_online_make_up_for_other_schools = models.BooleanField(default=True)
    available_places_for_make_up_online = models.IntegerField(default=3)
    available_places_for_make_up_on_site = models.IntegerField(default=3)

    def calculate_end_time_default(self):
        if self.start_time:
            end_time = (
                datetime.combine(
                    datetime.today(),
                    datetime.strptime(self.start_time, '%H:%M').time()
                    ) + timedelta(minutes=90)).time()
            return end_time
        return None

    def save(self, *args, **kwargs):
        if self.end_time is None:
            self.end_time = self.calculate_end_time_default()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.group_name


class StudentCourseSchedule(models.Model):
    course_schedule = models.ForeignKey(CourseSchedule, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    start_date = models.DateField(null=True, blank=True)

    class Meta:
        unique_together = ('course_schedule', 'student')

    def __str__(self) -> str:
        return self.student.__str__() + " " + self.course_schedule.group_name


class TrainerSchedule(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    year = models.IntegerField(default=datetime.now().year)
    week = models.IntegerField(default=1)
    date = models.DateField(null=True, blank=True)
    trainer = models.ForeignKey(Trainer, on_delete=models.CASCADE)
    available_day = models.ForeignKey(CourseDays, on_delete=models.SET_NULL, null=True, blank=True)
    available_hour_from = models.TimeField()
    available_hour_to = models.TimeField()
    online_only = models.BooleanField(default=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, null=True, blank=True)


class SchoolSchedule(models.Model):
    DAYS = (
        ("luni", "Luni"),
        ("marti", "Marti"),
        ("miercuri", "Miercuri"),
        ("joi", "Joi"),
        ("vineri", "Vineri"),
        ("sambata", "Sambata"),
        ("duminica", "Duminica"),
    )

    school = models.ForeignKey(School, on_delete=models.CASCADE, null=True, blank=True)
    working_day = models.CharField(max_length=20, choices=DAYS)
    start_hour = models.TimeField(null=False, blank=False)
    end_hour = models.TimeField(null=False, blank=False)


class DailySchoolSchedule(models.Model):
    blocked_by = (
        ("course", "Curs"),
        ("make_up", "Make Up"),
        ("other", "Other")
    )
    activity_type = (
        ("online", "Online"),
        ("sed", "Sediu"),
    )
    school_schedule = models.ForeignKey(SchoolSchedule, on_delete=models.CASCADE)
    date = models.DateField(null=False, blank=False)
    busy_from = models.TimeField(null=False, blank=False)
    busy_to = models.TimeField(null=False, blank=False)
    blocked_by = models.CharField(choices=blocked_by, null=False, blank=False, max_length=20)
    activity_type = models.CharField(activity_type, null=False, blank=False)
    room = models.ForeignKey(Room, on_delete=models.SET_NULL, null=True, blank=True)
    trainer_involved = models.ForeignKey(Trainer, on_delete=models.SET_NULL, null=True, blank=True)


class Session(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    course_session = models.ForeignKey(
        CourseSchedule,
        on_delete=models.CASCADE,
        related_name="sessions"
    )
    session_trainer = models.ForeignKey(
        Trainer,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="In case other trainer will replace a trainer",
    )
    session_passed = models.BooleanField(default=False)
    date = models.DateField()
    session_no = models.SmallIntegerField()

    def __str__(self) -> str:
        return f"{self.course_session} - {self.session_no}"


class SessionPresence(models.Model):
    STATUS = (
        ("present", "Present"),
        ("absent", "Absent"),
        ("made_up_complete", "Made Up Complete"),
        ("made_up_setup", "Made Up Setup"),
        ("made_up_absent", "Made Up Absent"),
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(Student, on_delete=models.SET_NULL, null=True, blank=True, related_name="student_presences")
    session = models.ForeignKey(Session, on_delete=models.SET_NULL, null=True, blank=True, related_name="session_presences")
    status = models.CharField(max_length=20, choices=STATUS)


class MakeUp(models.Model):
    TYPE = (
        ("onl", "Online"),
        ("hbr", "Hibrid"),
        ("sed", "Sediu"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    date_time = models.DateTimeField(null=True, blank=True)
    end_time = models.TimeField(default=None)
    online_link = models.CharField(max_length=500)
    type = models.CharField(
        max_length=50,
        choices=TYPE,
        null=True,
        blank=True)
    duration_in_minutes = models.SmallIntegerField(default=30)
    classroom = models.ForeignKey(Room, models.SET_NULL, blank=True, null=True)
    trainer = models.ForeignKey(
        Trainer, on_delete=models.SET_NULL, null=True, blank=True)
    make_up_approved = models.BooleanField(default=False)
    make_up_completed = models.BooleanField(default=False)
    can_be_used_as_online_make_up_for_other_schools = models.BooleanField(default=True)
    available_places_for_make_up_online = models.IntegerField(default=3)
    available_places_for_make_up_on_site = models.IntegerField(default=3)
    session = models.ForeignKey(Session, on_delete=models.SET_NULL, null=True, blank=True)

    def calculate_end_time(self):
        if self.date_time is not None:
            end_datetime = self.date_time + timedelta(minutes=self.duration_in_minutes)
            return end_datetime.time()
        return None

    def save(self, *args, **kwargs):
        if self.end_time is None:
            self.end_time = self.calculate_end_time()
        super().save(*args, **kwargs)


class AbsentStudent(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    absent_participant = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="student_absences",
        help_text="get all absences for student")
    absent_on_session = models.ForeignKey(
        Session,
        on_delete=models.CASCADE,
        related_name="session_absences",
        help_text="get all absences for session")
    is_absence_in_crm = models.BooleanField(default=False)
    is_absence_communicated_to_parent = models.BooleanField(default=False)
    is_absence_completed = models.BooleanField(
        default=False,
        help_text="if make up happened and student was not absent")
    is_absent_for_absence = models.BooleanField(
        null=True,
        blank=True,
        help_text="if student was absent for makeup",
    )
    has_make_up_scheduled = models.BooleanField(default=False)
    choosed_course_session_for_absence = models.ForeignKey(
        Session,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="course_session_absence",
        help_text="get absences setted up for session")
    choosed_make_up_session_for_absence = models.ForeignKey(
        MakeUp,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="make_up_absences",
        help_text="get absences setted up for make up")
    is_make_up_online = models.BooleanField(default=False)
    is_make_up_on_site = models.BooleanField(default=False)
    comment = models.TextField(max_length=500, null=True, blank=True)


class CourseDescription(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="course_description")
    short_description = models.TextField(max_length=100)
    long_description = models.TextField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True)


class SessionsDescription(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="session_descriptions")
    min_session_no_description = models.IntegerField(null=False, blank=False)
    max_session_no_description = models.IntegerField(null=False, blank=False)
    description = models.TextField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True)


class SentWhatsappMessages(models.Model):
    sent_on_time = models.TimeField(auto_now_add=True)
    sent_on_date = models.DateField(auto_now_add=True)
    sent_to_number = models.CharField(max_length=50)
    sent_message = models.TextField(max_length=500)
    has_errors = models.BooleanField(default=False)
    error_message = models.TextField(null=True, blank=True)


class SentEmailsMessages(models.Model):
    sent_on_time = models.TimeField(auto_now_add=True)
    sent_on_date = models.DateField(auto_now_add=True)
    sent_to_mail = models.CharField(max_length=100)
    sent_mail_subject = models.TextField(max_length=500)
    sent_mail_body = models.TextField(max_length=500)
    has_errors = models.BooleanField(default=False)
    error_message = models.TextField(null=True, blank=True)


class StudentInvoice(models.Model):
    PAYMENT_TYPE = (
        ("monthly", "Lunar"),
        ("module", "Semestrial"),
        ("yearly", "Anual"),
        ("four_courses", "La 4 cursuri"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(Student, on_delete=models.SET_NULL, null=True, blank=True)
    course_schedule = models.ForeignKey(CourseSchedule, on_delete=models.SET_NULL, null=True, blank=True)
    payment_frequency = models.CharField(max_length=50, choices=PAYMENT_TYPE)
    module_full_price = models.FloatField()
    invoice_price = models.FloatField()
    full_discount = models.FloatField()
    discount_details = models.CharField(max_length=100)
    invoice_with_student_found = models.BooleanField(default=False)
    smartbill_client = models.CharField(max_length=100, null=True)
    smarbill_cif = models.CharField(max_length=100, null=True)
    smarbill_email = models.CharField(max_length=100, null=True)
    smarbill_phone = models.CharField(max_length=100, blank=True)


class Invoice(models.Model):
    INVOICE_STATUS = (
        ('platita', 'Platita'),
        ('emisa', 'Emisa'),
        ('depasita', 'Depasita'),
        ('anulata', 'Anulata')
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student_invoice = models.ForeignKey(StudentInvoice, on_delete=models.CASCADE)
    invoice_no = models.CharField(max_length=50)
    invoice_status = models.CharField(max_length=20, choices=INVOICE_STATUS, null=True, blank=True)
    invoice_date_time = models.DateTimeField(default=datetime.now())


class News(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=50)
    short_description = models.CharField(max_length=100)
    text = models.TextField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    news_for_group = models.ForeignKey(CourseSchedule, null=True, blank=True, on_delete=models.SET_NULL)
    news_for_student = models.ForeignKey(Student, null=True, blank=True, on_delete=models.SET_NULL)


class Feedback(models.Model):
    FEEDBACK_FOR = (
        ('trainer', 'Trainer'),
        ('student', 'Student'),
        ('school', 'School'),
        ('course', 'Course')
    )
    feedback_for = models.CharField(null=False, blank=False, choices=FEEDBACK_FOR)
    