from django.urls import path

from app.views import SendEmailToGroupsView

urlpatterns = [
    path("send_group_email", SendEmailToGroupsView.as_view()),
]