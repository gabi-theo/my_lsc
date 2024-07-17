from django.urls import path

from app.views import (
    CheckUserRedirectView,
    ResetPasswordView,
    SignInView,
    SignOutView,
)

urlpatterns = [
    path("auth/login/", SignInView.as_view()),
    path("auth/logout/", SignOutView.as_view()),
    path("check_user/", CheckUserRedirectView.as_view()),
    path("auth/reset_password/",ResetPasswordView.as_view(),),
]