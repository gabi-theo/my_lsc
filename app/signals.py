from datetime import timedelta

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from app.models import CourseSchedule, Session, DaysOff


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
                )
                # sessions should be a week apart
                last_session_date_tried += timedelta(weeks=1)
            else:
                # convert datetime.date to datetime.datetime before subtraction
                last_session_date_tried += timedelta(weeks=1)
