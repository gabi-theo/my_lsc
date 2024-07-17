from rest_framework.generics import (
    CreateAPIView,
    ListCreateAPIView,
)
from rest_framework.permissions import IsAuthenticated

from app.serializers import (
    DaysOffSerializer,
    RoomSerializer,
    SchoolSetupSerializer,
)
from app.services.school import SchoolService


class DaysOffListView(ListCreateAPIView):
    serializer_class = DaysOffSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        school = self.request.user.user_school.all().first()
        queryset = SchoolService.get_days_off_for_school(school=school)
        return queryset

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.user_school.all().first())


class RoomListCreateView(ListCreateAPIView):
    serializer_class = RoomSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        school = self.request.user.user_school.all().first()
        queryset = SchoolService.get_rooms_by_school(school)
        return queryset

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.user_school.all().first())


class SchoolCreateView(CreateAPIView):
    serializer_class = SchoolSetupSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
