from uuid import uuid4
from datetime import datetime

from django.db import models


class Feedback(models.Model):
    FEEDBACK_FOR = (
        ('trainer', 'Trainer'),
        ('student', 'Student'),
        ('school', 'School'),
        ('course', 'Course'),
    )

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)

    feedback_for = models.CharField(null=False, blank=False, choices=FEEDBACK_FOR)
    recipient = models.CharField(max_length=50, null=False, blank=False, default="John Smith")
    role_of_submiter = models.CharField(max_length=10, null=False, blank=True, default="")

    content = models.CharField(max_length=500, null=False, blank=True)

    submited_by = models.ForeignKey("app.User", on_delete=models.SET_NULL, null=True)
    submited_for_student = models.ForeignKey("app.Student", on_delete=models.SET_NULL, null=True)
    feedback_for_school = models.ForeignKey("app.School", on_delete=models.SET_NULL, null=True)

    is_validated = models.BooleanField(null=False, blank=False, default=False)
    is_anonymised = models.BooleanField(null=False, blank=False, default=True)

    submission_date = models.DateField(auto_now_add=True)