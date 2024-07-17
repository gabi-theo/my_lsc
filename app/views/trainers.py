from rest_framework.generics import (
    GenericAPIView,
    ListAPIView,
    ListCreateAPIView,
)
from rest_framework.mixins import CreateModelMixin
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
)
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK

from app.permissions import (
    IsCoordinator,
)
from app.serializers import (
    TrainerCreateUpdateSerializer,
    TrainerFromSchoolSerializer,
    TrainerScheduleSerializer,
)
from app.services.trainers import TrainerService


class TrainersAvailabilityView(GenericAPIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        school = self.kwargs.get("school") if self.kwargs.get(
            "school") else self.request.user.user_school.all().first()
        trainers_availability = TrainerService.get_trainers_from_school_availability_by_date(
            school,
            self.kwargs.get("date"),
        )
        return Response(trainers_availability, status=HTTP_200_OK)


class TrainerCreateView(CreateModelMixin, GenericAPIView):
    serializer_class = TrainerCreateUpdateSerializer
    permission_classes = [IsAuthenticated, IsCoordinator]

    def post(self, request, *args, **kwargs):
        try:
            return self.create(request, *args, **kwargs)
        except Exception as e:
            print(e)


class TrainerFromSchoolListView(ListAPIView):
    serializer_class = TrainerFromSchoolSerializer

    def get_queryset(self):
        school = self.request.user.user_school.all().first()
        queryset = TrainerService.get_trainers_from_school(school)
        return queryset


class TrainerScheduleIntervalListCreateView(ListCreateAPIView):
    serializer_class = TrainerScheduleSerializer

    def get_queryset(self):
        school = self.request.user.user_school.all().first()
        queryset = TrainerService.get_trainer_from_school(
            school, self.kwargs["pk"])
        return queryset

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.user_school.all().first())
