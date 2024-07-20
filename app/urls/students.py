from django.urls import path

from app.views import (
    AbsentStudentsView,
    GetStudentByMailOrPhoneView,
    StudentAbsentView,
    StudentCoursesAndAbsentStatus,
    StudentCourseScheduleView,
    StudentPresenceView,
    StudentSessionAbsentView,
)

urlpatterns = [
    path("absent_students/", AbsentStudentsView.as_view()),
    path("student_courses_and_sessions_status/<uuid:student_id>/", StudentCoursesAndAbsentStatus.as_view()),
    path("get_student_by_email_or_phone/<str:email>/<str:phone>/", GetStudentByMailOrPhoneView.as_view()),
    path("students_presence/<uuid:student_id>/<uuid:course_schedule_id>/", StudentPresenceView.as_view()),
    path('student_courses/<str:student_id>/', StudentCourseScheduleView.as_view()),
    path("student_absent/<uuid:student_id>/<uuid:session_id>/", StudentAbsentView.as_view()),
    path("student_session_absent/<uuid:session_id>/", StudentSessionAbsentView.as_view()),
]