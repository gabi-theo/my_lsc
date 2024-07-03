from datetime import datetime, timedelta
from django.db.models import Q

from app.models import (
    AbsentStudent,
    MakeUp,
    Session,
    Trainer,
)
from app.services.school import SchoolService
from app.services.sessions import SessionService
from app.services.trainers import TrainerService
from app.utils import (
    get_date_of_day_in_same_week,
    create_serialized_response_from_object,
)
from my_lsc import settings



class MakeUpService:
    @staticmethod
    def get_make_up_by_id(pk):
        return MakeUp.objects.filter(pk=pk).first()

    @staticmethod
    def get_make_up_by_trainer_and_day(trainer, date):
        return MakeUp.objects.filter(
            trainer=trainer,
            date_time=date
        )

    @classmethod
    def create_empty_make_up_session_for_absence(cls, student, absence):        
        if not cls.get_make_up_for_student_by_session(student, absence).exists():
            make_up = MakeUp.objects.create(
                make_up_for_absence=absence,
            )
            make_up.students.add(student)

    @staticmethod
    def get_make_up_for_student_by_session(student, session):
        return MakeUp.objects.filter(make_up_for_absence__absent_on_session=session, students__in=[student])

    @staticmethod
    def create_make_up_from_trainer_schedule_data(data):
        trainer = Trainer.objects.get(id=data["trainer_id"])
        absent_student = AbsentStudent.objects.get(id=data["absent_id"])
        session = absent_student.absent_on_session
        date = data["date"]
        day = data["day"]
        correct_date = get_date_of_day_in_same_week(date, day)
        start_time = data["selected_start_time"]
        make_up, _ =MakeUp.objects.get_or_create(
            session=session,
            trainer=trainer,
            date_time= datetime.combine(correct_date, datetime.strptime(start_time, "%H:%M").time()),
            make_up_approved=True
        )
        absent_student.choosed_make_up_session_for_absence = make_up
        absent_student.has_make_up_scheduled = True
        absent_student.save()

    @staticmethod
    def get_make_ups_for_session(absence: AbsentStudent, school, type):
        available_sessions = []
        fields_to_include_for_serializer = [
            "id",
            "session__id",
            "session__session_no",
            "trainer",
            "date_time",
            "session__course_session__school__name",
            "online_link"]
        absence_session = absence.absent_on_session
        if settings.DEBUG:
            course_date = datetime(2024, 2, 1, 12, 0)
        else:
            course_date = datetime.now()
        matching_sessions = MakeUp.objects.filter(
            session__session_no=absence_session.session_no,
            session__course_session__course = absence_session.course_session.course,
            session__course_session__school=school,
            date_time__gte=course_date
        )
        if type == "onl":
            matching_sessions = matching_sessions.filter(type="onl")
        elif type == "sed":
            matching_sessions = matching_sessions.exclude(type="onl")

        for session in matching_sessions:
            if (
                session.make_up_absences.all().count() <
                session.available_places_for_make_up_on_site
            ):
                available_sessions.append(
                    create_serialized_response_from_object(object=session, fields=fields_to_include_for_serializer))
        return available_sessions

    @staticmethod
    def get_next_session_for_session(session):
        return Session.objects.filter(
            course_session=session.course_session, session_no=session.session_no+1)

    @staticmethod
    def get_next_session_date_from_current_session(next_session, current_session):
        if next_session.exists():
            next_session = next_session.first()
            return next_session.date
        return current_session.date + timedelta(days=7)

    @staticmethod
    def create_make_up_before_or_after_session_for_absence(absence: AbsentStudent, preference):
        next_session = MakeUpService.get_next_session_for_session(absence.absent_on_session)
        next_session_date = MakeUpService.get_next_session_date_from_current_session(
            next_session, absence.absent_on_session)
        next_session = next_session.first()
        if preference == "before":
            make_up_time = datetime.combine(next_session_date, absence.absent_on_session.course_session.start_time) + timedelta(minutes=90)
        else:
            make_up_time = datetime.combine(next_session_date, absence.absent_on_session.course_session.start_time) - timedelta(minutes=30)
        make_up, _ = MakeUp.objects.get_or_create(
                session=absence.absent_on_session,
                date_time=make_up_time,
            )
        return make_up

    @staticmethod
    def get_sessions_that_keep_interval_busy(
            date,
            start_interval,
            end_interval
    ):
        return Session.objects.filter(
            date=date,
        ).filter(
            Q(course_session__start_time__range=[start_interval, end_interval]) |
            Q(course_session__end_time__range=[start_interval, end_interval])
        )

    @staticmethod
    def get_make_ups_that_keep_interval_busy(
            date,
            start_interval,
            end_interval
    ):
        return MakeUp.objects.filter(
            date_time__date=date
        ).filter(
            Q(date_time__time__range=[start_interval, end_interval]) |
            Q(end_time__range=[start_interval, end_interval])
        )

    @staticmethod
    def is_make_up_possible_online_before_or_after_class_for_absence(absence, school):
        make_up_possible_before_session = False
        make_up_possible_after_session = False
        available_trainers_before = {}
        available_trainers_after = {}

        absent_session = absence.absent_on_session
        next_session = MakeUpService.get_next_session_for_session(absent_session)
        next_session_date = MakeUpService.get_next_session_date_from_current_session(next_session, absent_session)
        session_time = absent_session.course_session.start_time

        available_trainers_in_school_by_date = TrainerService.get_trainers_available_intervals_by_date_in_school(next_session_date, school)
        available_trainers_for_session_time = available_trainers_in_school_by_date.filter(
            available_hour_from__lte=session_time,
            available_hour_to__gte=session_time,
        )
        sessions_that_keeps_interval_for_make_up_busy_30_minutes_before = MakeUpService.get_sessions_that_keep_interval_busy(
            next_session_date,
            (datetime.combine(datetime.today(), session_time) - timedelta(minutes=30)).time(),
            session_time,
        )
        make_ups_that_keeps_interval_for_make_up_busy_30_minutes_before = MakeUpService.get_make_ups_that_keep_interval_busy(
            next_session_date,
            (datetime.combine(datetime.today(), session_time) - timedelta(minutes=30)).time(),
            session_time,
        )
        sessions_that_keeps_interval_for_make_up_busy_30_minutes_after = MakeUpService.get_sessions_that_keep_interval_busy(
            next_session_date,
            (datetime.combine(datetime.today(), session_time) + timedelta(minutes=90)).time(),
            (datetime.combine(datetime.today(), session_time) + timedelta(minutes=120)).time(),
        )
        make_ups_that_keeps_interval_for_make_up_busy_30_minutes_after = MakeUpService.get_make_ups_that_keep_interval_busy(
            next_session_date,
            (datetime.combine(datetime.today(), session_time) + timedelta(minutes=90)).time(),
            (datetime.combine(datetime.today(), session_time) + timedelta(minutes=120)).time(),
        )
        trainers_that_are_free_30_minutes_before = available_trainers_for_session_time.exclude(
            trainer__id__in=sessions_that_keeps_interval_for_make_up_busy_30_minutes_before.values_list('session_trainer__id', flat=True)
        ).exclude(trainer__id__in=make_ups_that_keeps_interval_for_make_up_busy_30_minutes_before.values_list('trainer__id', flat=True))
        trainers_that_are_free_30_minutes_after = available_trainers_for_session_time.exclude(
            trainer__id__in=sessions_that_keeps_interval_for_make_up_busy_30_minutes_after.values_list('session_trainer__id', flat=True)
        ).exclude(trainer__id__in=make_ups_that_keeps_interval_for_make_up_busy_30_minutes_after.values_list('trainer__id', flat=True))

        if trainers_that_are_free_30_minutes_before.exists():
            make_up_possible_before_session = True
            for trainer in trainers_that_are_free_30_minutes_before:
                available_trainers_before[str(trainer.id)] = f"{trainer.trainer.first_name} {trainer.trainer.last_name}"
        if trainers_that_are_free_30_minutes_after.exists():
            make_up_possible_after_session = True
            for trainer in trainers_that_are_free_30_minutes_after:
                available_trainers_after[str(trainer.id)] = f"{trainer.trainer.first_name} {trainer.trainer.last_name}"

        return {
            "make_up_possible_before_session": {
                "status": make_up_possible_before_session,
                "trainers": available_trainers_before,
                "date": next_session_date,
                "start": (datetime.combine(datetime.today(), session_time) - timedelta(minutes=30)).time(),
                "end": session_time,
            },
            "make_up_possible_after_session": {
                "status": make_up_possible_after_session,
                "trainers": available_trainers_before,
                "date": next_session_date,
                "start": (datetime.combine(datetime.today(), session_time) + timedelta(minutes=90)).time(),
                "end": (datetime.combine(datetime.today(), session_time) + timedelta(minutes=120)).time(),
            }
        }

    @staticmethod
    def is_make_up_possible_sed_before_or_after_class_for_absence(absence, school):
        make_up_possible_before_session = False
        make_up_possible_after_session = False
        available_trainers_before = {}
        available_trainers_after = {}
        available_rooms = SchoolService.get_rooms_by_school(school)

        absent_session = absence.absent_on_session
        next_session = MakeUpService.get_next_session_for_session(absent_session)
        next_session_date = MakeUpService.get_next_session_date_from_current_session(next_session, absent_session)
        session_time = absent_session.course_session.start_time

        available_trainers_in_school_by_date = TrainerService.get_trainers_available_intervals_by_date_in_school(
            next_session_date, school
        ).exclude(online_only=True)
        available_trainers_for_session_time = available_trainers_in_school_by_date.filter(
            available_hour_from__lte=session_time,
            available_hour_to__gte=session_time,
        )

        sessions_that_keeps_interval_for_make_up_busy_30_minutes_before = MakeUpService.get_sessions_that_keep_interval_busy(
            next_session_date,
            (datetime.combine(datetime.today(), session_time) - timedelta(minutes=30)).time(),
            session_time,
        ).exclude(course_session__course_type = "onl")
        make_ups_that_keeps_interval_for_make_up_busy_30_minutes_before = MakeUpService.get_make_ups_that_keep_interval_busy(
            next_session_date,
            (datetime.combine(datetime.today(), session_time) - timedelta(minutes=30)).time(),
            session_time,
        ).exclude(type = "onl")
        sessions_that_keeps_interval_for_make_up_busy_30_minutes_after = MakeUpService.get_sessions_that_keep_interval_busy(
            next_session_date,
            (datetime.combine(datetime.today(), session_time) + timedelta(minutes=90)).time(),
            (datetime.combine(datetime.today(), session_time) + timedelta(minutes=120)).time(),
        ).exclude(course_session__course_type = "onl")
        make_ups_that_keeps_interval_for_make_up_busy_30_minutes_after = MakeUpService.get_make_ups_that_keep_interval_busy(
            next_session_date,
            (datetime.combine(datetime.today(), session_time) + timedelta(minutes=90)).time(),
            (datetime.combine(datetime.today(), session_time) + timedelta(minutes=120)).time(),
        ).exclude(type = "onl")

        trainers_that_are_free_30_minutes_before = available_trainers_for_session_time.exclude(
            trainer__id__in=sessions_that_keeps_interval_for_make_up_busy_30_minutes_before.values_list('session_trainer__id', flat=True)
        ).exclude(trainer__id__in=make_ups_that_keeps_interval_for_make_up_busy_30_minutes_before.values_list('trainer__id', flat=True))
        trainers_that_are_free_30_minutes_after = available_trainers_for_session_time.exclude(
            trainer__id__in=sessions_that_keeps_interval_for_make_up_busy_30_minutes_after.values_list('session_trainer__id', flat=True)
        ).exclude(trainer__id__in=make_ups_that_keeps_interval_for_make_up_busy_30_minutes_after.values_list('trainer__id', flat=True))

        if trainers_that_are_free_30_minutes_before.exists() and (
            sessions_that_keeps_interval_for_make_up_busy_30_minutes_before.count() + make_ups_that_keeps_interval_for_make_up_busy_30_minutes_before.count() < available_rooms.count()
        ):
            make_up_possible_before_session = True
            for trainer in trainers_that_are_free_30_minutes_before:
                available_trainers_before[str(trainer.id)] = trainer.__str__()
        if trainers_that_are_free_30_minutes_after.exists() and (
            sessions_that_keeps_interval_for_make_up_busy_30_minutes_after.count() + make_ups_that_keeps_interval_for_make_up_busy_30_minutes_after.count() < available_rooms.count()
        ):
            make_up_possible_after_session = True
            for trainer in trainers_that_are_free_30_minutes_after:
                available_trainers_after[str(trainer.id)] = trainer.__str__()

        return {
            "make_up_possible_before_session": {
                "status": make_up_possible_before_session,
                "trainers": available_trainers_before,
                "date": next_session_date,
                "start": (datetime.combine(datetime.today(), session_time) - timedelta(minutes=30)).time(),
                "end": session_time,
            },
            "make_up_possible_after_session": {
                "status": make_up_possible_after_session,
                "trainers": available_trainers_before,
                "date": next_session_date,
                "start": (datetime.combine(datetime.today(), session_time) + timedelta(minutes=90)).time(),
                "end": (datetime.combine(datetime.today(), session_time) + timedelta(minutes=120)).time(),
            }
        }