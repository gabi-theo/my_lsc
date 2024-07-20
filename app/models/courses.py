from uuid import uuid4
from datetime import (
    datetime,
    timedelta,
)

from django.db import models


class Course(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    next_possible_course = models.ManyToManyField(
        'self',
        blank=True,
        symmetrical=False,
        related_name='next_course'
    )
    course_type = models.CharField(max_length=50, null=False, blank=False)

    def __str__(self) -> str:
        return str(self.course_type)


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

    def __str__(self):
        return str(self.day)


class CourseDescription(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    course = models.ForeignKey(
        "app.Course", on_delete=models.CASCADE, related_name="course_description")
    short_description = models.TextField(max_length=100)
    long_description = models.TextField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True)


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

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    course = models.ForeignKey(
        "app.Course", on_delete=models.CASCADE, related_name='course_schedules')
    school = models.ForeignKey(
        "app.School",
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
    classroom = models.ForeignKey("app.Room", models.SET_NULL, blank=True, null=True)
    default_trainer = models.ForeignKey(
        "app.Trainer", on_delete=models.SET_NULL, null=True, blank=True)
    students = models.ManyToManyField(
        "app.Student",
        related_name="course_schedule_students",
        through='StudentCourseSchedule',
    )
    course_type = models.CharField(max_length=10, choices=TYPE)
    online_link = models.CharField(max_length=500, null=True, blank=True)
    can_be_used_as_online_make_up_for_other_schools = models.BooleanField(
        default=True)
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
        return str(self.group_name)
