from django.urls import path

from app.views import (
    CheckUserRedirectView,
    RegisterView,
    ResetPasswordView,
    SignInView,
    SignOutView,
    ActivateAccountView,
)

urlpatterns = [
    path("auth/login/", SignInView.as_view()),
    path("auth/logout/", SignOutView.as_view()),
    path("check_user/", CheckUserRedirectView.as_view()),
    path("auth/reset_password/",ResetPasswordView.as_view(),),
    path("auth/register/", RegisterView.as_view()),
    path("activate/<uidb64>/<token>/<parent_id>/", ActivateAccountView.as_view(), name='activate'),
]