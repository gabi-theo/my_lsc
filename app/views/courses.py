from datetime import datetime

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.generics import (
    GenericAPIView,
    ListAPIView,
    UpdateAPIView,
)
from rest_framework.response import Response
from rest_framework.views import APIView

from app.serializers import CourseScheduleSerializer
from app.services.courses import CourseService
from app.services.dailyschoolschedule import DailySchoolScheduleService
from app.services.sessions import SessionService


class CourseScheduleDetailView(ListAPIView, GenericAPIView):
    serializer_class = CourseScheduleSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['id']

    def get_queryset(self):
        school = self.request.user.user_school.first()
        return CourseService.get_courses_from_school(school)


class DailySchoolScheduleAPIView(APIView):
    def get(self, request, format=None, *args, **kwargs):

        school_id = self.kwargs.get('school_id')

        response = DailySchoolScheduleService.get_suitable_make_up_intervals(
            school_id=school_id)

        return Response(response)

    def post(self, request, format=None, *args, **kwargs):

        print(request.data)

        absence_id = request.data.get("absence_id")

        start_date = datetime.strptime(
            request.data.get("start_date"), "%Y-%m-%d").date()

        start_time = datetime.strptime(
            request.data.get("start_time"), "%H:%M:%S").time()

        response = DailySchoolScheduleService.assign_make_up(
            absence_id=absence_id, start_date=start_date, start_time=start_time)

        return Response(response)


class CourseScheduleUpdate(UpdateAPIView):
    queryset = CourseService.get_all_course_schedules()
    serializer_class = CourseScheduleSerializer
    lookup_field = 'pk'

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        data = request.data.copy()

        if data.get('classroom') == '---':
            del data['classroom']

        if data.get('default_trainer') == '---':
            del data['default_trainer']

        serializer = self.get_serializer(instance, data=data, partial=True)

        if serializer.is_valid():
            serializer.save()
            SessionService.update_default_trainer_for_course_session(
                course_session_id=self.kwargs["pk"],
                trainer_id=request.data["default_trainer"],
            )
            return Response({"message": "Course schedule successfuly updated"})

        else:
            return Response({"message": "failed", "details": serializer.errors})


class CourseScheduleListView(ListAPIView):
    serializer_class = CourseScheduleSerializer

    def get_queryset(self):
        school = self.request.user.user_school.first()
        return CourseService.get_courses_from_school(school=school)
