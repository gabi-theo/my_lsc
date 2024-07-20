from uuid import uuid4

from django.db import models


class School(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    user = models.ForeignKey(
        "app.User",
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
        return str(self.name)
    

class DaysOff(models.Model):
    first_day_off = models.DateField()
    last_day_off = models.DateField()
    day_off_info = models.CharField(max_length=200)
    school = models.ForeignKey("app.School", on_delete=models.CASCADE)


class Room(models.Model):
    room_name = models.CharField(max_length=50, null=False, blank=False, default="room name")
    capacity = models.SmallIntegerField()
    school = models.ForeignKey("app.School", on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f"{self.school} - {self.room_name} - {self.capacity}"
    

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

    school = models.ForeignKey("app.School", on_delete=models.CASCADE, null=True, blank=True)
    working_day = models.CharField(max_length=20, choices=DAYS)
    start_hour = models.TimeField(null=False, blank=False)
    end_hour = models.TimeField(null=False, blank=False)


class DailySchoolSchedule(models.Model):
    BLOCKED_BY = (
        ("course", "Curs"),
        ("make_up", "Make Up"),
        ("other", "Other")
    )
    ACTIVITY_TYPE = (
        ("online", "Online"),
        ("sed", "Sediu"),
    )
    school_schedule = models.ForeignKey("app.SchoolSchedule", on_delete=models.CASCADE)
    date = models.DateField(null=False, blank=False)
    busy_from = models.TimeField(null=False, blank=False)
    busy_to = models.TimeField(null=False, blank=False)
    blocked_by = models.CharField(choices=BLOCKED_BY, null=False, blank=False, max_length=20)
    activity_type = models.CharField(choices=ACTIVITY_TYPE, null=False, blank=False)
    room = models.ForeignKey(Room, on_delete=models.SET_NULL, null=True, blank=True)
    trainer_involved = models.ForeignKey("app.Trainer", on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.school_schedule.working_day}, {self.date}, ({self.busy_from} - {self.busy_to}): ({self.activity_type}, {self.room}, {self.blocked_by}, {self.trainer_involved})"