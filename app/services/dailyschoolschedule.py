from app.models import DailySchoolSchedule, MakeUp

from app.services.trainers import TrainerService
from app.services.school import SchoolService
from app.services.absences import AbsenceService

from app.utils import intervals_intersect

from my_lsc.settings import DEBUG

from datetime import datetime, timedelta


class DailySchoolScheduleService:

    MAKE_UP_LOOKAHEAD_DAYS = 30

    @staticmethod
    def get_daily_school_schedule_by_school_and_date(school, date):
        return DailySchoolSchedule.objects.filter(
            school_schedule__school=school,
            date=date,
        )

    @staticmethod
    def get_suitable_make_up_intervals(school_id):
        """
        Returns available intervals for manually scheduling a make up session.
        """

        school = SchoolService.get_school_by_id(school_id=school_id)

        rooms = SchoolService.get_rooms_by_school(
            school).values_list('room_name', flat=True,)
        room_count = rooms.count()

        response = {"sed": {}, "onl": {}}

        for activity_type in ("sed", "onl"):

            date = datetime(2024, 2, 1) if DEBUG else datetime.now()

            for _ in range(DailySchoolScheduleService.MAKE_UP_LOOKAHEAD_DAYS):

                school_schedules = DailySchoolScheduleService.get_daily_school_schedule_by_school_and_date(
                    school=school,
                    date=date,
                ).order_by('activity_type', 'busy_from')

                # Filter DailySchoolSchedule for the given date and weekday
                response[activity_type][str(date.date())] = TrainerService.get_trainer_intervals(
                    school=school, date=date, school_schedules=school_schedules)

                date = date + timedelta(days=1)

        # eliminate intervals that cannot happen due to busy rooms
        # TODO: test this functionality as fake data don't provide enough data for this to be tested
        intervals_to_be_removed = []

        for date_interval in response["sed"]:

            interval_schedules = DailySchoolScheduleService.get_daily_school_schedule_by_school_and_date(
                school=school,
                date=datetime.strptime(date_interval, "%Y-%m-%d").date()
            ).filter(
                activity_type="sed"
            ).order_by(
                'busy_from'
            )

            if not interval_schedules.exists():
                continue

            rooms_intervals = list(interval_schedules.values_list(
                "busy_from", "busy_to"))

            for trainer_key in response["sed"][date_interval]:

                intervals_to_be_removed = []

                for interval in response["sed"][date_interval][trainer_key]["free"]:

                    busy_intervals = [
                        (interval["start"], interval["end"]) for start, end in rooms_intervals
                        if intervals_intersect(interval["start"], interval["end"], start, end)
                    ]

                    if len(busy_intervals) >= room_count:
                        intervals_to_be_removed.extend(busy_intervals)

                response["sed"][date_interval][trainer_key]["free"] = sorted(
                    [
                        {
                            "start": start_time,
                            "end": end_time
                        } for start_time, end_time in
                        set(
                            map(
                                lambda interval: (
                                    interval["start"], interval["end"]),
                                response["sed"][date_interval][trainer_key]["free"]
                            )
                        ).difference(intervals_to_be_removed)
                    ],
                    key=lambda interval: interval["start"]
                )

        return response

    @staticmethod
    def assign_make_up(absence_id, start_date, start_time):

        absence = AbsenceService.get_absence_by_id(absence_id=absence_id)

        session = absence.absent_on_session

        trainer = session.session_trainer

        activity_type = session.course_session.course_type

        classroom = session.course_session.classroom

        make_up = MakeUp.objects.create(
            date_time=datetime.combine(start_date, start_time),
            type=activity_type,
            classroom=classroom,
            trainer=trainer,
            session=session
        )

        return {"makeup_id": make_up.id}
