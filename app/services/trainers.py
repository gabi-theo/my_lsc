from datetime import datetime, timedelta

from app.models import TrainerFromSchool, TrainerSchedule, User, Session, MakeUp
from app.utils import random_password_generator, find_available_times
from core.tasks import send_trainer_registration_email


class TrainerService:
    @staticmethod
    def get_trainer_from_school(school, trainer_id):
        return TrainerSchedule.objects.filter(school=school, trainer__id=trainer_id)

    @staticmethod
    def get_trainers_from_school(school):
        return TrainerFromSchool.objects.filter(school=school)

    @staticmethod
    def create_user_for_trainer_and_send_emai(username, trainer_email):
        password = random_password_generator()
        user_try = 1
        while User.objects.filter(username=username.lower()).exists():
            username = f"{username.lower()}{user_try}"
            user_try = int(user_try) + 1
        try:
            user = User.objects.create_user(
                username=username.lower(),
                password=password,
                is_reset_password_needed=True,
                role="trainer",
            )
        except Exception as e:
            print(e)
        send_trainer_registration_email.delay(
            email=trainer_email,
            username=username,
            password=password)
        return user

    @staticmethod
    def build_trainer_calendar_from_schedule(trainer, interval, week, year):
        calendar = {}
        unavailable_time = []
        sessions = Session.objects.filter(
            session_trainer=trainer,
            date=interval.date
        )
        make_ups = MakeUp.objects.filter(
            trainer=trainer,
            date_time=interval.date
        )

        for session in sessions:
            initial_start_time = session.course_session.start_time
            start_time = datetime.combine(session.date, initial_start_time)
            end_time = datetime.combine(session.date, initial_start_time) + timedelta(minutes=90)
            unavailable_time.append({
                "start": start_time.time(),
                "end": end_time.time(),
                "type": "curs",
                "grupa": session.course_session.group_name,
            })
        for make_up in make_ups:
            start_time = make_up.date_time
            end_time = start_time + timedelta(minutes=30)
            unavailable_time.append({
                "start": start_time.time(),
                "end": end_time.time(),
                "type": "recuperare",
                "grupa": "make up",
            })
        trainer_start_time = interval.available_hour_from
        trainer_end_time = interval.available_hour_to
        calendar[interval.available_day.day] = {
            "available_intervals": find_available_times(trainer_start_time, trainer_end_time, unavailable_time),
            "unavailable_intervals": unavailable_time, 
        }
        return calendar

    @staticmethod
    def get_trainers_from_school_availability_by_date(school, date):
        trainers_availability = {}
        if isinstance(date, str):
            date = datetime.strptime(date, "%Y-%m-%d").date()
        week = date.isocalendar()[1]
        year = date.year
        available_trainers = TrainerSchedule.objects.filter(
            school=school,
            date=date)
        for interval_for_trainer in available_trainers:
            trainer_calendar = TrainerService.build_trainer_calendar_from_schedule(
                interval_for_trainer.trainer, interval_for_trainer, week, year
            )
            trainer = f"{interval_for_trainer.trainer.first_name} {interval_for_trainer.trainer.last_name}"
            if not trainers_availability.get(trainer):
                trainers_availability[trainer] = {
                    "trainer_id": interval_for_trainer.trainer.id,
                    "date": interval_for_trainer.date,
                    "year": year,
                    "days_available": trainer_calendar,
                }
            
            else:
                trainers_availability[trainer]["days_available"][interval_for_trainer.available_day.day]["available_intervals"] += trainer_calendar[interval_for_trainer.available_day.day]["available_intervals"] 
                trainers_availability[trainer]["days_available"][interval_for_trainer.available_day.day]["unavailable_intervals"] += trainer_calendar[interval_for_trainer.available_day.day]["unavailable_intervals"] 

        return trainers_availability
    
    @staticmethod
    def get_trainers_available_intervals_by_date_in_school(date, school):
        if isinstance(date, str):
            date = datetime.strptime(date, "%Y-%m-%d").date()
        return TrainerSchedule.objects.filter(
            school=school,
            date=date,
            is_available=True
        )
