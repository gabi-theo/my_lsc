from django.urls import path

from app.views import (
    CourseScheduleDetailView,
    CourseScheduleListView,
    CourseScheduleUpdate,
)

urlpatterns = [
    path("course_schedule/", CourseScheduleListView.as_view()),
    path('course_schedule/<uuid:pk>/update/', CourseScheduleUpdate.as_view()),
    path("course_schedule_details/", CourseScheduleDetailView.as_view()),
]
