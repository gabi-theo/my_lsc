from uuid import uuid4

from django.db import models


class News(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    title = models.CharField(max_length=50)
    short_description = models.CharField(max_length=100)
    text = models.TextField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)
    school = models.ForeignKey("app.School", on_delete=models.CASCADE)
    news_for_group = models.ForeignKey("app.CourseSchedule", null=True, blank=True, on_delete=models.SET_NULL)
    news_for_student = models.ForeignKey("app.Student", null=True, blank=True, on_delete=models.SET_NULL)