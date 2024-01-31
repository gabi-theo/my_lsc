from datetime import datetime
from rest_framework import status
from rest_framework.response import Response

from app.models import Session, SessionPresence, Trainer
from app.utils import create_serialized_response_from_object


class SessionService:
    @staticmethod
    def get_sessions_by_user_school(user):
        return Session.objects.filter(course_session__school=user.user_school.all().first())

    @staticmethod
    def get_session_by_course_schedule_id(course_schedule_id):
        return Session.objects.filter(course_session__id=course_schedule_id)

    @staticmethod
    def get_sessions_by_trainer_and_date(trainer, date):
        return Session.objects.filter(
            session_trainer=trainer,
            date=date
        )

    @staticmethod
    def get_presence_by_course_and_student(course_schedule, student):
        return SessionPresence.objects.filter(student=student, session__course_session=course_schedule)

    @staticmethod
    def update_default_trainer_for_course_session(course_session_id, trainer_id):
        sessions = Session.objects.filter(course_session__id=course_session_id)
        trainer = Trainer.objects.get(id=trainer_id)
        for session in sessions:
            session.session_trainer = trainer
            session.save()

    @staticmethod
    def get_sessions_by_school(school):
        return Session.objects.filter(course_session__school=school)

    @staticmethod
    def get_session_by_id(session_id):
        try:
            return Session.objects.filter(pk=session_id)
        except Session.DoesNotExist:
            return Response({'detail': 'Session not found'}, status=status.HTTP_404_NOT_FOUND)

    @staticmethod
    def get_next_sessions_for_absence(absence, school, type):
        available_sessions = []
        fields_to_include_for_serializer = [
            "id",
            "course_session__id",
            "session_no",
            "session_trainer",
            "date",
            "course_session__start_time",
            "course_session__school__name",
            "course_session__online_link",
            "course_session__available_places_for_make_up_online",
            "course_session__available_places_for_make_up_on_site"]
        absence_session = absence.absent_on_session

        matching_sessions = Session.objects.filter(
            session_no=absence_session.session_no,
            course_session__course = absence_session.course_session.course,
            date__gte=datetime.now()
        ).exclude(id=absence_session.id).order_by("date")

        school_sessions = matching_sessions.filter(
            course_session__school=school,
        )
        if type != "sed":
            other_school_sessions = matching_sessions.exclude(
                id__in=school_sessions,
            ).filter(course_session__can_be_used_as_online_make_up_for_other_schools=True)
            for session in other_school_sessions:
                if (
                    session.course_session_absence.all().count() <
                    session.course_session.available_places_for_make_up_online
                ):
                    available_sessions.append(
                        create_serialized_response_from_object(object=session, fields=fields_to_include_for_serializer))
        for session in school_sessions:
            if (
                session.course_session_absence.all().count() <
                session.course_session.available_places_for_make_up_online or 
                session.course_session_absence.all().count() <
                session.course_session.available_places_for_make_up_on_site
            ):
                available_sessions.append(
                    create_serialized_response_from_object(object=session, fields=fields_to_include_for_serializer))
        return available_sessions