from django.urls import path

from app.views import (
    TrainersAvailabilityView,
    TrainerCreateView,
    TrainerFromSchoolListView,
    TrainerScheduleIntervalListCreateView,
)

urlpatterns = [
    path("trainers_from_school/", TrainerFromSchoolListView.as_view()),
    path("trainer_create/", TrainerCreateView.as_view()),
    path("trainer_schedule_interval/<uuid:pk>/", TrainerScheduleIntervalListCreateView.as_view()),
    path("trainers_availability/<str:date>/<str:school>/", TrainersAvailabilityView.as_view()),
]