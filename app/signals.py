from datetime import timedelta, time
import datetime

from django.core.exceptions import ObjectDoesNotExist
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from app.models import CourseDays, CourseSchedule, Session, DaysOff, DailySchoolSchedule, SchoolSchedule, MakeUp, TrainerSchedule


@receiver(post_save, sender=CourseSchedule)
def create_session(sender, instance, created, **kwargs):
    if created:
        # manually keep track of assigned sessions and the last assigned session since we might need to push some back
        sessions_assigned = 0
        last_session_date_tried = instance.first_day_of_session

        # used for string -> int and int -> string conversions
        weekdays = ("luni", "marti", "miercuri", "joi",
                    "vineri", "sambata", "duminica")

        # ensure we assign the session to the correct day
        if weekdays[last_session_date_tried.weekday()] != instance.day:
            last_session_date_tried += timedelta(days=(weekdays.index(instance.day) -
                                                    last_session_date_tried.weekday()) % 7)

        # query database once, then use the query to perform checks
        time_off_periods = DaysOff.objects.filter(
            school=instance.school,
            first_day_off__lte=instance.last_day_of_session,
            last_day_off__gte=instance.first_day_of_session
        )

        # do not assign more sessions than specified by the schedule
        while sessions_assigned < instance.total_sessions:

            # check that the session doesn't start when it's time off
            time_off = time_off_periods.filter(
                first_day_off__lte=last_session_date_tried,
                last_day_off__gte=last_session_date_tried
            )

            if not time_off:

                # don't assign sessions past the last day of the course schedule
                if last_session_date_tried > instance.last_day_of_session:
                    break  # very graceful handling

                # all good, create session
                sessions_assigned += 1
                Session.objects.create(
                    course_session=instance,
                    date=last_session_date_tried,
                    session_no=sessions_assigned,
                    session_trainer=instance.default_trainer if instance.default_trainer else None
                )
                try:
                    school_schedule = SchoolSchedule.objects.get(school=instance.school, working_day=instance.day)
                except ObjectDoesNotExist:
                    school_schedule = SchoolSchedule.objects.create(school=instance.school, working_day=instance.day, start_hour=time(9,0), end_hour=time(21,0))
                DailySchoolSchedule.objects.create(
                    school_schedule=school_schedule,
                    date=last_session_date_tried,
                    busy_from=instance.start_time,
                    busy_to=instance.end_time,
                    blocked_by="course",
                    activity_type=instance.course_type,
                    room=instance.classroom,
                    trainer_involved=instance.default_trainer if instance.default_trainer else None,
                )
                last_session_date_tried: datetime.datetime
                instance: CourseSchedule
                # sessions should be a week apart
                last_session_date_tried += timedelta(weeks=1)
            else:
                # convert datetime.date to datetime.datetime before subtraction
                last_session_date_tried += timedelta(weeks=1)


@receiver(post_save, sender=MakeUp)
def create_daily_schedule_from_makeup(sender, instance: MakeUp, created, **kwargs):
    weekdays = ("luni", "marti", "miercuri", "joi",
                    "vineri", "sambata", "duminica")
    if created:
        day = weekdays[instance.date_time.date().weekday()]
        try:
            school_schedule = SchoolSchedule.objects.get(school=instance.session.course_session.school, working_day=day)
        except ObjectDoesNotExist:
            school_schedule = SchoolSchedule.objects.create(school=instance.session.course_session.school, working_day=day, start_hour=time(9,0), end_hour=time(21,0))
        DailySchoolSchedule.objects.get_or_create(
                    school_schedule=school_schedule,
                    date=instance.date_time.date(),
                    busy_from=instance.date_time.time(),
                    busy_to=instance.end_time,
                    blocked_by="make_up",
                    activity_type=instance.type,
                    room=instance.classroom,
                    trainer_involved=instance.trainer,
                )
