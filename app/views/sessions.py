from json import (
    JSONDecodeError,
    loads,
)

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.generics import (
    GenericAPIView,
    ListAPIView,
    RetrieveAPIView,
)
from rest_framework.mixins import CreateModelMixin
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK
from rest_framework.views import APIView

from app.models import (
    School,
    TrainerFromSchool,
)
from app.permissions import (
    IsCoordinator,
    IsTrainer,
)
from app.serializers import (
    MakeUpSerializer,
    SessionListSerializer,
    SessionSerializer,
)
from app.services.absences import AbsenceService
from app.services.makeups import MakeUpService
from app.services.sessions import SessionService


class MakeUpChooseView(GenericAPIView):
    def post(self, request, *args, **kwargs):
        # TODO: IMPLEMENT 30 MINS MAKE-UPS
        session = None
        make_up = None
        absence = AbsenceService.get_absence_by_id(self.kwargs['absence_id'])
        if self.kwargs.get("session_option") and self.kwargs.get("session_option") != "None":
            session = SessionService.get_session_by_id(
                self.kwargs.get("session_option")).first()
            absence.choosed_course_session_for_absence = session
        elif self.kwargs.get("make_up_option") and self.kwargs.get("make_up_option") != "None":
            if self.kwargs.get("make_up_option") == "before" or self.kwargs.get("make_up_option") == "after":
                make_up = MakeUpService.create_make_up_before_or_after_session_for_absence(
                    absence, self.kwargs.get("make_up_opton"))
            else:
                make_up = MakeUpService.get_make_up_by_id(
                    self.kwargs.get("make_up_option"))
            absence.choosed_make_up_session_for_absence = make_up
        absence.has_make_up_scheduled = True
        absence.is_absent_for_absence = None
        absence.save()
        # TODO: IMPLEMENT SEND MAIL FOR MAKE UP CONFIRMATION
        return Response({"message": "Absence updated"}, status=HTTP_200_OK)


class MakeUpSessionsAvailableView(CreateModelMixin, GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = MakeUpSerializer

    def get(self, request, *args, **kwargs):
        make_up_type = self.kwargs.get('make_up_type')  # onl, sed, any
        absence_id = self.kwargs.get('absence_id')
        school_id = self.kwargs.get('school_id')
        absence = AbsenceService.get_absence_by_id(absence_id)

        if not school_id:
            if request.user.is_anonymous:
                school = absence.absent_on_session.course_session.school
            else:
                if request.user.role == "stud":
                    school = request.user.parent_user.school.first()
                elif request.user.role == "coordinator":
                    school = request.user.user_school.first()
                else:
                    trainer = request.user.trainer_user
                    school = TrainerFromSchool.objects.filter(
                        trainer=trainer).schools.first()
        else:
            school = School.objects.get(pk=school_id)
        make_up_options = {
            "onl": {
                "courses": [],
                "make_ups": [],
                "30_mins": [],
            },
            "sed": {
                "courses": [],
                "make_ups": [],
                "30_mins": [],
            },
        }
        if make_up_type == "onl":
            make_up_options["onl"]["make_ups"] = MakeUpService.get_make_ups_for_session(
                absence, school, type=make_up_type)
            make_up_options["onl"]["courses"] = SessionService.get_next_sessions_for_absence(
                absence, school, make_up_type)
            make_up_options["onl"]["30_mins"] = \
                MakeUpService.is_make_up_possible_online_before_or_after_class_for_absence(
                    absence, school)

        elif make_up_type == "sed":
            make_up_options["sed"]["make_ups"] = MakeUpService.get_make_ups_for_session(
                absence, school, type=make_up_type)
            make_up_options["sed"]["courses"] = SessionService.get_next_sessions_for_absence(
                absence, school, make_up_type)
            make_up_options["sed"]["30_mins"] = \
                MakeUpService.is_make_up_possible_sed_before_or_after_class_for_absence(
                    absence, school)
        return Response(make_up_options, status=HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)


class MakeUpTrainerScheduleView(GenericAPIView):
    def post(self, request, *args, **kwargs):
        try:
            data = loads(request.body.decode('utf-8'))
            MakeUpService.create_make_up_from_trainer_schedule_data(data)
            return Response({'message': 'Make up created'}, status=HTTP_200_OK)
        except JSONDecodeError:
            return Response({'error': 'Invalid JSON data'}, status=HTTP_200_OK)


class SessionInfoList(RetrieveAPIView, GenericAPIView):
    serializer_class = SessionSerializer

    def get_queryset(self):
        return SessionService.get_sessions_by_school(self.request.user.user_school.first())

    def retrieve(self, request, *args, **kwargs):
        session = SessionService.get_session_by_id(self.kwargs['pk']).first()
        serializer = self.get_serializer(session)
        return Response(serializer.data, status=HTTP_200_OK)


class StudentMakeUpAbsentView(APIView):
    def post(self, request, *args, **kwargs):
        absence = AbsenceService.get_absence_by_id(kwargs["absence_id"])
        if kwargs["presence_type"] == "present":
            absence.is_absence_completed = True
            absence.is_absent_for_absence = False
        elif kwargs["presence_type"] == "absent":
            absence.is_absent_for_absence = True
            absence.is_absence_completed = False
        absence.save()
        return Response({"Presence updated"}, status=HTTP_200_OK)


class SessionCourseListView(ListAPIView):
    serializer_class = SessionSerializer

    def get_queryset(self):
        return SessionService.get_session_by_course_schedule_id(self.kwargs['pk'])


class SessionsListView(ListAPIView):
    serializer_class = SessionListSerializer
    permission_classes = [IsAuthenticated, IsCoordinator or IsTrainer]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['date']

    def get_queryset(self):
        return SessionService.get_sessions_by_user_school(
            self.request.user)
