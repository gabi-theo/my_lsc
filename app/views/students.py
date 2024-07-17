from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.generics import ListAPIView
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
)
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_404_NOT_FOUND,
)
from rest_framework.views import APIView

from app.filters import AbsenceFilter
from app.models import (
    CourseSchedule,
    SessionPresence,
)
from app.permissions import (
    IsCoordinator,
    IsTrainer,
)
from app.serializers import (
    AbsencesSerializer,
    CourseScheduleSerializer,
    SessionPresenceSerializer,
)
from app.services.absences import AbsenceService
from app.services.courses import CourseService
from app.services.makeups import MakeUpService
from app.services.sessions import SessionService
from app.services.students import StudentService


class AbsentStudentsView(ListAPIView):
    serializer_class = AbsencesSerializer
    permission_classes = [IsAuthenticated, IsCoordinator or IsTrainer]
    filter_backends = [DjangoFilterBackend]
    filterset_class = AbsenceFilter

    def get_queryset(self):
        return AbsenceService.get_all_absences_from_school(
            self.request.user.user_school.all().first())


class GetStudentByMailOrPhoneView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *arg, **kwargs):
        phone = kwargs["phone"]
        email = kwargs["email"]
        students = StudentService.get_students_id_by_phone_or_email(
            phone, email)
        if students.exists():
            students_response = []
            for student in students:
                students_response.append(
                    {"student_id": student.id, "student_name": student.__str__()})
            return Response({"students": students_response}, status=HTTP_200_OK)
        return Response({"error": "student_not_found"}, status=HTTP_404_NOT_FOUND)


class StudentCourseScheduleView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, student_id):
        try:
            student_courses = CourseSchedule.objects.filter(
                students__id=student_id)
            serializer = CourseScheduleSerializer(student_courses, many=True)
            return Response(serializer.data, status=HTTP_200_OK)
        except CourseSchedule.DoesNotExist:
            return Response({"error": "Student not found"}, status=HTTP_404_NOT_FOUND)


class StudentCoursesAndAbsentStatus(APIView):
    permission_classes = [AllowAny]

    def get(self, request, student_id):
        student_courses = CourseSchedule.objects.filter(
            students__id=student_id)
        resp = []
        for course in student_courses:
            student_sessions_in_course = []
            for session in course.sessions.all():
                absence = AbsenceService.get_absence_by_missed_session_id_and_student_id(
                    session_id=session.id, student_id=student_id)
                print(session.id)
                print(student_id)
                print(absence)
                presence_status = SessionPresence.objects.filter(
                    student__id=student_id, session=session)
                student_sessions_in_course.append({
                    "session_id": session.id,
                    "session_date": session.date,
                    "session_number": session.session_no,
                    "presence_status": presence_status.first().status if presence_status.exists() else None,
                    "absence_id": absence.id if absence else None,
                })

            resp.append(
                {
                    "course_schedule_id": course.id,
                    "course_schedule_name": course.group_name,
                    "sessions": student_sessions_in_course
                }
            )

        return Response(resp, status=HTTP_200_OK)


class StudentAbsentView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        student = StudentService.get_student_by_id(kwargs['student_id'])
        session = SessionService.get_session_by_id(
            kwargs["session_id"]).first()
        absence, created = AbsenceService.create_absent_student_for_session(
            student=student,
            session=session,)
        if created:
            MakeUpService.create_empty_make_up_session_for_absence(
                student, absence)
        return Response({"Student marked successfully as absent"}, status=HTTP_200_OK)

    def get(self, request, *args, **kwargs):
        if not request.user.is_anonymous and request.user.role == "coordinator":
            absences = AbsenceService.get_all_absences_from_school(
                school=request.user.user_school.first())
            serializer = AbsencesSerializer(absences, many=True)
            return Response(serializer.data)
        else:
            absence = AbsenceService.get_absence_by_missed_session_id_and_student_id(
                kwargs['session_id'],
                kwargs['student_id'],
            )
            serializer = AbsencesSerializer(absence)
            return Response(serializer.data)


class StudentPresenceView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        student = StudentService.get_student_by_id(kwargs["student_id"])
        course_schedule = CourseService.get_course_schedule_by_pk(
            kwargs["course_schedule_id"])
        session_presences = SessionService.get_presence_by_course_and_student(
            course_schedule, student)

        serializer = SessionPresenceSerializer(session_presences, many=True)

        return Response(serializer.data, status=HTTP_200_OK)


class StudentSessionAbsentView(ListAPIView):
    serializer_class = AbsencesSerializer

    def get_queryset(self):
        return AbsenceService.get_absences_by_session_id(self.kwargs["session_id"])
