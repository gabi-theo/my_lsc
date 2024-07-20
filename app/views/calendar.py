from datetime import (
    datetime,
    timedelta,
)

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from app.services.calendar import CalendarService

from my_lsc.settings import DEBUG


class SchoolCalendarView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        school_id = kwargs.get("school_id")
        student_id = kwargs.get("student_id")

        if not DEBUG:
            start_date = datetime.today().date()
        else:
            start_date = datetime(2024, 4, 10)

        end_date = start_date + timedelta(days=30)
        user = request.user

        calendar_data = CalendarService.generate_calendar(
            user, school_id, student_id, start_date, end_date)

        return Response(calendar_data)
