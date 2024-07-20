from django.db import models


class Feedback(models.Model):
    FEEDBACK_FOR = (
        ('trainer', 'Trainer'),
        ('student', 'Student'),
        ('school', 'School'),
        ('course', 'Course')
    )
    feedback_for = models.CharField(null=False, blank=False, choices=FEEDBACK_FOR)