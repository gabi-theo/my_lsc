import json
from django.db.models import Min, Max
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from rest_framework import generics, status, mixins
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from app.models import News
from datetime import datetime, timedelta
from itertools import groupby

from my_lsc import settings

from app.authentication import CookieJWTAuthentication
from app.filters import AbsenceFilter
from app.models import Session, CourseSchedule, DailySchoolSchedule, Room, School, SessionPresence, TrainerFromSchool, TrainerSchedule

from app.permissions import IsCoordinator, IsTrainer, IsStudent

from app.serializers import (
    AbsencesSerializer,
    CourseScheduleSerializer,
    DaysOffSerializer,
    ImportSerializer,
    MakeUpSerializer,
    NewsSerializer,
    ResetPasswordSerializer,
    RoomSerializer,
    SchoolSetupSerializer,
    SessionSerializer,
    SessionListSerializer,
    SessionPresenceSerializer,
    SignInSerializer,
    StudentsEmailSerializer,
    TrainerCreateUpdateSerializer,
    TrainerFromSchoolSerializer,
    TrainerScheduleSerializer,
    SessionForCalendarSerializer,
)
from app.services.calendar import CalendarService
from app.services.absences import AbsenceService
from app.services.courses import CourseService
from app.services.makeups import MakeUpService
from app.services.news import NewsService
from app.services.school import SchoolService
from app.services.sessions import SessionService
from app.services.students import StudentService
from app.services.trainers import TrainerService
from app.services.users import UserService
from app.services.dailyschoolschedule import DailySchoolScheduleService

from app.utils import check_excel_format_in_request_data

########################################## AUTH VIEW
class SignInView(generics.GenericAPIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    serializer_class = SignInSerializer

    def post(self, request: Request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = UserService.get_user_by_username(
            serializer.validated_data["username"])
        user.save()
        response = Response(self.get_serializer(user).data)
        CookieJWTAuthentication.login(user, response)
        return response


class SignOutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(request):
        response = Response({"message": "Bye, see you soon 😌"})
        response.delete_cookie(settings.AUTH_COOKIE_KEY)

        return response


class CheckUserRedirectView(APIView):
    def get(self, request):
        redirect_url = ""
        if request.user.role == "coordinator" and not request.user.user_school.all().exists():
            redirect_url = "http://127.0.0.1:5500/lsc_frontend_simplified/school_create.html"
        elif request.user.role == "parent":
            # TODO: implement
            pass
        else:
            redirect_url = "http://127.0.0.1:5500/lsc_frontend_simplified/today_sessions.html"
        return Response({"redirect_to": redirect_url}, status=status.HTTP_200_OK)


class ResetPasswordView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated, IsCoordinator | IsTrainer]
    serializer_class = ResetPasswordSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        response = Response({"message": "Password Reset Successfully"})
        user.set_password(serializer.validated_data.get("password"))
        user.is_reset_password_needed = False
        user.save()

        return response
 



################################################### SCHOOL VIEW
class DaysOffListView(generics.ListCreateAPIView):
    serializer_class = DaysOffSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        school = self.request.user.user_school.all().first()
        queryset = SchoolService.get_days_off_for_school(school=school)
        return queryset

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.user_school.all().first())


class RoomListCreateView(generics.ListCreateAPIView):
    serializer_class = RoomSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        school = self.request.user.user_school.all().first()
        queryset = SchoolService.get_rooms_by_school(school)
        return queryset

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.user_school.all().first())


class SchoolCreateView(generics.CreateAPIView):
    serializer_class = SchoolSetupSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


####################################################### COURSES AND SESSIONS VIEWS
class CourseScheduleDetailView(generics.ListAPIView, generics.GenericAPIView):
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

        start_date = datetime.strptime(request.data.get("start_date"), "%Y-%m-%d").date()

        start_time = datetime.strptime(request.data.get("start_time"), "%H:%M:%S").time()

        response = DailySchoolScheduleService.assign_make_up(absence_id=absence_id, start_date=start_date, start_time=start_time)

        return Response(response)


class CourseScheduleUpdate(generics.UpdateAPIView):
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


class CourseScheduleListView(generics.ListAPIView):
    serializer_class = CourseScheduleSerializer

    def get_queryset(self):
        school = self.request.user.user_school.first()
        return CourseService.get_courses_from_school(school=school)


class MakeUpChooseView(generics.GenericAPIView):
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
        return Response({"message": "Absence updated"}, status=status.HTTP_200_OK)


class MakeUpSessionsAvailableView(mixins.CreateModelMixin, generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = MakeUpSerializer
    
    def get(self, request, *args, **kwargs):
        make_up_type = self.kwargs.get('make_up_type') # onl, sed, any
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
                    school = TrainerFromSchool.objects.filter(trainer=trainer).schools.first()
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
            make_up_options["onl"]["courses"] =  SessionService.get_next_sessions_for_absence(
                absence, school, make_up_type)
            make_up_options["onl"]["30_mins"] = \
                MakeUpService.is_make_up_possible_online_before_or_after_class_for_absence(absence, school)
            
        elif make_up_type == "sed":
            make_up_options["sed"]["make_ups"] = MakeUpService.get_make_ups_for_session(
                absence, school, type=make_up_type)
            make_up_options["sed"]["courses"] =  SessionService.get_next_sessions_for_absence(
                absence, school, make_up_type)
            make_up_options["sed"]["30_mins"] = \
                MakeUpService.is_make_up_possible_sed_before_or_after_class_for_absence(absence, school)
        return Response(make_up_options, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)


class MakeUpTrainerScheduleView(generics.GenericAPIView):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body.decode('utf-8'))
            MakeUpService.create_make_up_from_trainer_schedule_data(data)
            return Response({'message': 'Make up created'}, status=status.HTTP_200_OK)
        except json.JSONDecodeError:
            return Response({'error': 'Invalid JSON data'}, status=status.HTTP_200_OK)


class SendEmailToGroupsView(generics.GenericAPIView):
    serializer_class = StudentsEmailSerializer
    permission_classes = [IsAuthenticated, IsCoordinator]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if serializer.validated_data["send_mail"]:
            StudentService.send_emails_to_students_in_groups(
                groups=serializer.validated_data["groups"],
                subject=serializer.validated_data["subject"],
                message=serializer.validated_data["message"],
            )
        return Response({"message": "Mails sent successfully"}, status.HTTP_200_OK)


class SessionInfoList(generics.RetrieveAPIView, generics.GenericAPIView):
    serializer_class = SessionSerializer

    def get_queryset(self):
        return SessionService.get_sessions_by_school(self.request.user.user_school.first())

    def retrieve(self, request, *args, **kwargs):
        session = SessionService.get_session_by_id(self.kwargs['pk']).first()
        serializer = self.get_serializer(session)
        return Response(serializer.data, status=status.HTTP_200_OK)


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
        return Response({"Presence updated"}, status=status.HTTP_200_OK)


class SessionCourseListView(generics.ListAPIView):
    serializer_class = SessionSerializer

    def get_queryset(self):
        return SessionService.get_session_by_course_schedule_id(self.kwargs['pk'])


class SessionsListView(generics.ListAPIView):
    serializer_class = SessionListSerializer
    permission_classes = [IsAuthenticated, IsCoordinator or IsTrainer]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['date']

    def get_queryset(self):
        return SessionService.get_sessions_by_user_school(
            self.request.user)


class UploadCourseExcelView(APIView):
    serializer_class = ImportSerializer
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        check_excel_format_in_request_data(request)
        school = self.request.user.user_school.all().first()
        try:
            total_courses = CourseService.create_course_and_course_schedule_from_excel_by_school(
                request.data['file'], school)
            return Response({'message': f'Total cursuri create: {total_courses}'}, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# TRAINERS VIEWS
class TrainersAvailabilityView(generics.GenericAPIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        school = self.kwargs.get("school") if self.kwargs.get(
            "school") else self.request.user.user_school.all().first()
        trainers_availability = TrainerService.get_trainers_from_school_availability_by_date(
            school,
            self.kwargs.get("date"),
        )
        return Response(trainers_availability, status=status.HTTP_200_OK)


class TrainerCreateView(mixins.CreateModelMixin, generics.GenericAPIView):
    serializer_class = TrainerCreateUpdateSerializer
    permission_classes = [IsAuthenticated, IsCoordinator]

    def post(self, request, *args, **kwargs):
        try:
            return self.create(request, *args, **kwargs)
        except Exception as e:
            print(e)


class TrainerFromSchoolListView(generics.ListAPIView):
    serializer_class = TrainerFromSchoolSerializer

    def get_queryset(self):
        school = self.request.user.user_school.all().first()
        queryset = TrainerService.get_trainers_from_school(school)
        return queryset


class TrainerScheduleIntervalListCreateView(generics.ListCreateAPIView):
    serializer_class = TrainerScheduleSerializer

    def get_queryset(self):
        school = self.request.user.user_school.all().first()
        queryset = TrainerService.get_trainer_from_school(
            school, self.kwargs["pk"])
        return queryset

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.user_school.all().first())


# STUDENTS VIEWS
class AbsentStudentsView(generics.ListAPIView):
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
            return Response({"students": students_response}, status=status.HTTP_200_OK)
        return Response({"error": "student_not_found"}, status=status.HTTP_404_NOT_FOUND)


class StudentCourseScheduleView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, student_id):
        try:
            student_courses = CourseSchedule.objects.filter(
                students__id=student_id)
            serializer = CourseScheduleSerializer(student_courses, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except CourseSchedule.DoesNotExist:
            return Response({"error": "Student not found"}, status=status.HTTP_404_NOT_FOUND)


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

        return Response(resp, status=status.HTTP_200_OK)


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
        return Response({"Student marked successfully as absent"}, status=status.HTTP_200_OK)

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

        return Response(serializer.data, status=status.HTTP_200_OK)


class StudentSessionAbsentView(generics.ListAPIView):
    serializer_class = AbsencesSerializer

    def get_queryset(self):
        return AbsenceService.get_absences_by_session_id(self.kwargs["session_id"])


class UploadStudentsExcelView(APIView):
    serializer_class = ImportSerializer
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        check_excel_format_in_request_data(request)
        school = self.request.user.user_school.all().first()
        try:
            StudentService.create_student_from_excel_and_assign_it_to_school_course(
                request.data['file'],
                school,
            )
            return Response({'message': 'Data imported successfully'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

################################ NEWS VIEW
class NewsView(generics.ListAPIView):
    serializer_class = NewsSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.request.method == 'POST':
            self.permission_classes = [IsAuthenticated, IsCoordinator]
        elif self.request.method == 'DELETE':
            self.permission_classes = [IsAuthenticated, IsCoordinator]
        elif self.request.method == 'GET':
            self.permission_classes = [IsAuthenticated, IsCoordinator | IsTrainer | IsStudent]
        return super(NewsView, self).get_permissions()

    def post(self, request, *args, **kwargs):
        
        serializer = NewsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def get(self, request, *args, **kwargs):
        school_id = kwargs.get("school_id")
        student_id = kwargs.get("student_id")
            
        if not school_id:
            return Response({"error": "school_id required"}, status=status.HTTP_400_BAD_REQUEST)

        if student_id:
            news_queryset_by_student = NewsService.get_news_by_student_and_school(school_id, student_id)
        
        serializer = NewsSerializer(news_queryset_by_student, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def delete(self, request, *args, **kwargs):
            news_id = kwargs.get("news_id")
            
            if not news_id:
                return Response({"error": "news_id required"}, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                news = NewsService.get_news_by_news_id(news_id)
            except News.DoesNotExist:
                return Response({"error": "News not found"}, status=status.HTTP_404_NOT_FOUND)
            
            news.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    def get_queryset(self):
        return NewsService.get_news_by_school(self.request.user.user_school.all().first())


################################################# SCHOOL CALENDAR VIEW
class SchoolCalendarView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        school_id = kwargs.get("school_id")
        student_id = kwargs.get("student_id")
        
        if not settings.DEBUG: 
            start_date = datetime.today().date()
        else:
            start_date = datetime(2024, 4, 10)
        
        end_date = start_date + timedelta(days=30)
        user = request.user

        calendar_data = CalendarService.generate_calendar(user, school_id, student_id, start_date, end_date)

        return Response(calendar_data)
    
