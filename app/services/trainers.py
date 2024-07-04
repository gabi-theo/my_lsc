from datetime import datetime, timedelta

from app.models import (
    TrainerFromSchool,
    TrainerSchedule,
    User,
    Session,
    MakeUp,
    Trainer,
)

from app.utils import (
    random_password_generator,
    find_available_times,
    interval_duration_gte,
)

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
        )
    
    @staticmethod
    def get_trainer_intervals(
        school,
        date,
        school_schedules,
        ) -> dict[str, dict[str, dict | str]]:
        """
        
        Returns the intervals for trainers which match the schedule of the school, for a given date.
        Free intervals can be optionally filtered.

        The format is

        {
            "<trainer_id>-<trainer_first_name>-<trainer_last_name>":

            {
                "busy":

                {
                    "start": <interval_start> (datetime.time),
                    "end": <interval_end> (datetime.time),
                    "type": <schedule_type> (string), <See `DailySchooSchedule.blocked_by`>
                }

                "free":

                {
                    "start": <interval_start> (datetime.time),
                    "end": <interval_end> (datetime.time)
                }

                "schedule": "<start_time> - <end_time>" (string)
            }
        }
        
        :param school: The school for which to get trainer intervals

        :param date: The date for which to get trainer intervals
        """

        result = {}

        trainer_schedules = TrainerService.get_trainers_available_intervals_by_date_in_school(school=school, date=date)

        last_schedule_type = None

        for trainer_schedule in trainer_schedules:

            intervals = {"busy": [], "free": [], "schedule":None}
            trainer_start = trainer_schedule.available_hour_from
            trainer_end = trainer_schedule.available_hour_to
            school_schedule = list(school_schedules.filter(trainer_involved=trainer_schedule.trainer).order_by('busy_from'))
            last_interval_end_busy = None
            intervals["schedule"] = f"{trainer_start} - {trainer_end}"

            for schedule_idx, schedule in enumerate(school_schedule):

                schedule_start = schedule.busy_from
                schedule_end = schedule.busy_to
                schedule_type = schedule.blocked_by

                if schedule_start == trainer_start:
                    # This is a busy interval with the course starting right at the start of the trainer's schedule
                    intervals["busy"].append({"start": schedule_start, "end": schedule_end, "type": schedule_type})

                elif schedule_idx == 0:
                    # This is the free interval between the start of the trainer's schedule and the start of the first course

                    if interval_duration_gte(trainer_start, schedule_start, timedelta(minutes=30)):
                        # Interval is at least 30m, can potentially be used for a make up
                        interval_start = trainer_start
                        interval_end = schedule_start
                        
                        if schedule_type == "course":
                            # If the current activty is a course, leave the 30m slot before it open
                            # for the usual course-related make up
                            interval_end = (datetime.combine(datetime.today(), interval_end) - timedelta(minutes=30)).time()

                        if interval_duration_gte(interval_start, interval_end, timedelta(minutes=30)):
                            # If, after accounting for the usual time slot(s),
                            # there is still enough time for a make-up, add this interval as free
                            intervals["free"].append({"start": interval_start, "end": interval_end})

                    intervals["busy"].append({"start": schedule_start, "end": schedule_end, "type": schedule_type})
                elif last_interval_end_busy == schedule_start:
                    # no break, intervals one after the other, extend busy interval
                    intervals["busy"][-1]["end"] = schedule_end
                elif last_interval_end_busy != schedule_start:
                    # This is a free interval between two courses

                    if interval_duration_gte(last_interval_end_busy, schedule_start, timedelta(minutes=30)):
                        # Interval is at least 30m, can potentially be used for a make up

                        interval_start = last_interval_end_busy
                        interval_end = schedule_start

                        prev_schedule_type = None

                        if schedule_idx > 0:
                            prev_schedule_type = school_schedule[schedule_idx - 1].blocked_by

                        if prev_schedule_type == "course":
                            # If the previous activty was a course, leave the 30m slot after it open
                            # for the usual course-related make up
                            interval_start = (datetime.combine(datetime.today(), interval_start) + timedelta(minutes=30)).time()

                        if schedule_type == "course":
                            # If the current activty is a course, leave the 30m slot before it open
                            # for the usual course-related make up
                            interval_end = (datetime.combine(datetime.today(), interval_end) - timedelta(minutes=30)).time()

                        if interval_duration_gte(interval_start, interval_end, timedelta(minutes=30)):
                            # If, after accounting for the usual time slot(s),
                            # there is still enough time for a make-up, add this interval as free
                            intervals["free"].append({"start": interval_start, "end": interval_end})

                    intervals["busy"].append({"start": schedule_start, "end": schedule_end, "type": schedule_type})

                last_interval_end_busy = schedule_end
                last_schedule_type = schedule_type

            if not last_interval_end_busy:
                last_interval_end_busy = trainer_start
            if last_interval_end_busy != trainer_end:
                if interval_duration_gte(last_interval_end_busy, trainer_end, timedelta(minutes=30)):
                        # Interval is at least 30m, can potentially be used for a make up
                        interval_start = last_interval_end_busy
                        interval_end = trainer_end
                        
                        if last_schedule_type == "course":
                            # If the last activty is a course, leave the 30m slot after it open
                            # for the usual course-related make up
                            interval_start = (datetime.combine(datetime.today(), interval_start) + timedelta(minutes=30)).time()

                        if interval_duration_gte(interval_start, interval_end, timedelta(minutes=30)):
                            # If, after accounting for the usual time slot(s),
                            # there is still enough time for a make-up, add this interval as free
                            intervals["free"].append({"start": interval_start, "end": interval_end})

            result[f"{trainer_schedule.trainer.id}-{trainer_schedule.trainer.first_name}-{trainer_schedule.trainer.last_name}"] = intervals

        return result
    

    @staticmethod
    def get_trainer_by_username(username: str):
        return Trainer.objects.filter(user__username=username).first()

    @staticmethod
    def get_trainer_by_id(trainer_id):
        return Trainer.objects.filter(pk=trainer_id).first()
    def get_trainer_by_user(user):
        return Trainer.objects.get(user=user)
