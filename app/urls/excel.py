from django.urls import path

from app.views import (
    UploadCourseExcelView,
    UploadStudentsExcelView,
)

urlpatterns = [
    path("course_excel_upload/", UploadCourseExcelView.as_view()),
    path("students_excel_upload/", UploadStudentsExcelView.as_view()),
]