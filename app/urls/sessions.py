from django.urls import path

from app.views import (
    MakeUpChooseView,
    MakeUpSessionsAvailableView,
    MakeUpTrainerScheduleView,
    SessionCourseListView,
    SessionInfoList,
    SessionsListView,
    StudentMakeUpAbsentView,
)

urlpatterns = [
    path("course_sessions/<uuid:pk>/",SessionInfoList.as_view()),
    path("get_available_make_ups/<uuid:school_id>/<uuid:absence_id>/<str:make_up_type>/", MakeUpSessionsAvailableView.as_view()),
    path("sessions_from_course/<uuid:pk>/", SessionCourseListView.as_view()),
    path("make_up_choose/<str:absence_id>/<str:session_option>/<str:make_up_option>/<str:mins_option_30>/<str:send_email>/", MakeUpChooseView.as_view()),
    path("make_up_from_trainer_schedule/", MakeUpTrainerScheduleView.as_view()),
    path("make_up_presence/<uuid:absence_id>/<str:presence_type>/", StudentMakeUpAbsentView.as_view()),
    path("sessions/", SessionsListView.as_view()),
]