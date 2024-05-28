from django.urls import path

from app.views import (
    AbsentStudentsView,
    CheckUserRedirectView,
    CourseScheduleDetailView,
    CourseScheduleListView,
    CourseScheduleUpdate,
    DailySchoolScheduleAPIView,
    DaysOffListView,
    GetStudentByMailOrPhoneView,
    MakeUpChooseView,
    MakeUpSessionsAvailableView,
    MakeUpTrainerScheduleView,
    NewsView,
    ResetPasswordView,
    RoomListCreateView,
    SchoolCreateView,
    SendEmailToGroupsView,
    SessionsListView,
    SessionCourseListView,
    SessionInfoList,
    SignInView,
    SignOutView,
    StudentAbsentView,
    StudentCourseScheduleView,
    StudentCoursesAndAbsentStatus,
    StudentMakeUpAbsentView,
    StudentPresenceView,
    StudentSessionAbsentView,
    TrainersAvailabilityView,
    TrainerCreateView,
    TrainerFromSchoolListView,
    TrainerScheduleIntervalListCreateView,
    UploadCourseExcelView,
    UploadStudentsExcelView,
)


urlpatterns = [
    ################################ AUTH ENDPOINTS
    path("auth/login/", SignInView.as_view()),
    path("auth/logout/", SignOutView.as_view()),
    path("check_user/", CheckUserRedirectView.as_view()),
    path("auth/reset_password/",ResetPasswordView.as_view(),),

    ################################ SCHOOL ENDPOINTS
    path("days_off/", DaysOffListView.as_view()),
    path("rooms/", RoomListCreateView.as_view()),
    path("school_create/", SchoolCreateView.as_view()),
    path("news/", NewsView.as_view()),
    path("school_schedules/", DailySchoolScheduleAPIView.as_view()),

    ################################ COURSES AND SESSIONS ENDPOINTS
    path("course_schedule/", CourseScheduleListView.as_view()),
    path('course_schedule/<uuid:pk>/update/', CourseScheduleUpdate.as_view()),
    path("course_schedule_details/", CourseScheduleDetailView.as_view()),
    path("course_sessions/<uuid:pk>/",SessionInfoList.as_view()),
    path("course_excel_upload/", UploadCourseExcelView.as_view()),
    path("get_available_make_ups/<uuid:absence_id>/<str:make_up_type>", MakeUpSessionsAvailableView.as_view()),
    path("sessions_from_course/<uuid:pk>/", SessionCourseListView.as_view()),
    path("make_up_choose/<str:absence_id>/<str:session_option>/<str:make_up_option>/<str:mins_option_30>/<str:send_email>/", MakeUpChooseView.as_view()),
    path("make_up_from_trainer_schedule/", MakeUpTrainerScheduleView.as_view()),
    path("make_up_presence/<uuid:absence_id>/<str:presence_type>/", StudentMakeUpAbsentView.as_view()),
    path("send_group_email", SendEmailToGroupsView.as_view()),
    path("sessions/", SessionsListView.as_view()),

    ################################ TRAINERS ENDPOINTS
    path("trainers_from_school/", TrainerFromSchoolListView.as_view()),
    path("trainer_create/", TrainerCreateView.as_view()),
    path("trainer_schedule_interval/<uuid:pk>/", TrainerScheduleIntervalListCreateView.as_view()),
    path("trainers_availability/<str:date>/<str:school>/", TrainersAvailabilityView.as_view()),

    ################################ STUDENTS ENDPOINTS
    path("absent_students/", AbsentStudentsView.as_view()),
    path("student_courses_and_sessions_status/<uuid:student_id>/", StudentCoursesAndAbsentStatus.as_view()),
    path("get_student_by_email_or_phone/<str:email>/<str:phone>/", GetStudentByMailOrPhoneView.as_view()),
    path("students_presence/<uuid:student_id>/<uuid:course_schedule_id>/", StudentPresenceView.as_view()),
    path('student_courses/<str:student_id>/', StudentCourseScheduleView.as_view()),
    path("students_excel_upload/", UploadStudentsExcelView.as_view()),
    path("student_absent/<uuid:student_id>/<uuid:session_id>/", StudentAbsentView.as_view()),
    path("student_session_absent/<uuid:session_id>/", StudentSessionAbsentView.as_view()),
]
