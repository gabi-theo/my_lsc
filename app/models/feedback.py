from uuid import uuid4
from datetime import datetime

from django.db import models


class Feedback(models.Model):
    FEEDBACK_FOR = (
        ('trainer', 'Trainer'),
        ('student', 'Student'),
        ('school', 'School'),
        ('course', 'Course')
    )
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    feedback_for = models.CharField(null=False, blank=False, choices=FEEDBACK_FOR, max_length=50)
    recipient = models.CharField(max_length=50, null=False, blank=False, default="John Smith")
    submission_date = models.DateField(auto_now_add=True)
    content = models.CharField(max_length=500, null=False, blank=False, default="Lorem Ipsum")
    is_validated = models.BooleanField(default=False)
