from uuid import uuid4

from django.db import models


class Parent(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    school = models.ForeignKey(
        "app.School",
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        related_name="school_students",
    )
    user = models.OneToOneField(
        "app.User", on_delete=models.SET_NULL, null=True, blank=True, related_name="parent_user")
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
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    parent = models.ForeignKey("app.Parent", on_delete=models.CASCADE, related_name="children")
    first_name = models.CharField(max_length=50, null=False, blank=False)
    last_name = models.CharField(max_length=50, null=False, blank=False)

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}"
    

class StudentCourseSchedule(models.Model):
    course_schedule = models.ForeignKey("app.CourseSchedule", on_delete=models.CASCADE)
    student = models.ForeignKey("app.Student", on_delete=models.CASCADE)
    start_date = models.DateField(null=True, blank=True)

    class Meta:
        unique_together = ('course_schedule', 'student')

    def __str__(self) -> str:
        return self.student.__str__() + " " + str(self.course_schedule.group_name)