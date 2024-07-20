from django.urls import path

from app.views import SchoolCalendarView

urlpatterns = [
    path("school_calendar/<uuid:school_id>/<uuid:student_id>/", SchoolCalendarView.as_view()),
    path("school_calendar/<uuid:school_id>/", SchoolCalendarView.as_view()),
]