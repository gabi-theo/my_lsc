from django.urls import path

from app.views import (
    CheckUserRedirectView,
    RegisterView,
    ResetPasswordView,
    SignInView,
    SignOutView,
)

urlpatterns = [
    path("auth/login/", SignInView.as_view()),
    path("auth/logout/", SignOutView.as_view()),
    path("check_user/", CheckUserRedirectView.as_view()),
    path("auth/reset_password/",ResetPasswordView.as_view(),),
    path("auth/register/", RegisterView.as_view()),
]