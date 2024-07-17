from uuid import uuid4
from datetime import datetime

from django.db import models


class Trainer(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    user = models.OneToOneField(
        "app.User", on_delete=models.CASCADE, null=True, related_name="trainer_user")
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone_contact = models.CharField(max_length=50)
    email_contact = models.EmailField()

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}"
    

class TrainerFromSchool(models.Model):
    school = models.ForeignKey("app.School", on_delete=models.SET_NULL, null=True, blank=True, related_name="school_trainers")
    trainer = models.ForeignKey("app.Trainer", on_delete=models.CASCADE)


class TrainerSchedule(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    year = models.IntegerField(default=datetime.now().year)
    week = models.IntegerField(default=1)
    date = models.DateField(null=True, blank=True)
    trainer = models.ForeignKey("app.Trainer", on_delete=models.CASCADE)
    available_day = models.ForeignKey("app.CourseDays", on_delete=models.SET_NULL, null=True, blank=True)
    available_hour_from = models.TimeField()
    available_hour_to = models.TimeField()
    online_only = models.BooleanField(default=False)
    school = models.ForeignKey("app.School", on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"{self.trainer.first_name} {self.trainer.last_name} available on {self.available_day}, {self.date} from {self.available_hour_from} to {self.available_hour_to}"