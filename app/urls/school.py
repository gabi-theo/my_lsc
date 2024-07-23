from django.urls import path

from app.views import (
    DailySchoolScheduleAPIView,
    DaysOffListView,
    NewsView,
    RoomListCreateView,
    SchoolCreateView,
)

urlpatterns = [
    path("days_off/", DaysOffListView.as_view()),
    path("rooms/", RoomListCreateView.as_view()),
    path("school_create/", SchoolCreateView.as_view()),
    path("news/<uuid:school_id>/<uuid:student_id>/", NewsView.as_view()),
    path("school_schedules/<uuid:school_id>/",
         DailySchoolScheduleAPIView.as_view()),
]
