from uuid import uuid4
from datetime import timedelta

from django.db import models


class Session(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    course_session = models.ForeignKey(
        "app.CourseSchedule",
        on_delete=models.CASCADE,
        related_name="sessions"
    )
    session_trainer = models.ForeignKey(
        "app.Trainer",
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
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    student = models.ForeignKey("app.Student", on_delete=models.SET_NULL,
                                null=True, blank=True, related_name="student_presences")
    session = models.ForeignKey("app.Session", on_delete=models.SET_NULL,
                                null=True, blank=True, related_name="session_presences")
    status = models.CharField(max_length=20, choices=STATUS)


class MakeUp(models.Model):
    TYPE = (
        ("onl", "Online"),
        ("hbr", "Hibrid"),
        ("sed", "Sediu"),
    )

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    date_time = models.DateTimeField(null=True, blank=True)
    end_time = models.TimeField(default=None)
    online_link = models.CharField(max_length=500)
    type = models.CharField(
        max_length=50,
        choices=TYPE,
        null=True,
        blank=True)
    duration_in_minutes = models.SmallIntegerField(default=30)
    classroom = models.ForeignKey(
        "app.Room", models.SET_NULL, blank=True, null=True)
    trainer = models.ForeignKey(
        "app.Trainer",
        on_delete=models.SET_NULL,
        null=True,
        blank=True)
    make_up_approved = models.BooleanField(default=False)
    make_up_completed = models.BooleanField(default=False)
    can_be_used_as_online_make_up_for_other_schools = models.BooleanField(
        default=True)
    available_places_for_make_up_online = models.IntegerField(default=3)
    available_places_for_make_up_on_site = models.IntegerField(default=3)
    session = models.ForeignKey(
        "app.Session",
        on_delete=models.SET_NULL,
        null=True,
        blank=True)

    def calculate_end_time(self):
        if self.date_time is not None:
            end_datetime = self.date_time + \
                timedelta(minutes=self.duration_in_minutes)
            return end_datetime.time()
        return None

    def save(self, *args, **kwargs):
        if self.end_time is None:
            self.end_time = self.calculate_end_time()
        super().save(*args, **kwargs)


class AbsentStudent(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    absent_participant = models.ForeignKey(
        "app.Student",
        on_delete=models.CASCADE,
        related_name="student_absences",
        help_text="get all absences for student")
    absent_on_session = models.ForeignKey(
        "app.Session",
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
        "app.Session",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="course_session_absence",
        help_text="get absences setted up for session")
    choosed_make_up_session_for_absence = models.ForeignKey(
        "app.MakeUp",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="make_up_absences",
        help_text="get absences setted up for make up")
    is_make_up_online = models.BooleanField(default=False)
    is_make_up_on_site = models.BooleanField(default=False)
    comment = models.TextField(max_length=500, null=True, blank=True)


class SessionsDescription(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    course = models.ForeignKey(
        "app.Course", on_delete=models.CASCADE, related_name="session_descriptions")
    min_session_no_description = models.IntegerField(null=False, blank=False)
    max_session_no_description = models.IntegerField(null=False, blank=False)
    description = models.TextField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True)
