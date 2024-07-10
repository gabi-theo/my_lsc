from datetime import timedelta
from rest_framework.response import Response
from rest_framework import generics, status, mixins
from django.shortcuts import get_object_or_404
from app.models import Session
from app.services.sessions import SessionService
from app.services.school import SchoolService
from app.services.trainers import TrainerService
from app.services.students import StudentService
from app.serializers import SessionForCalendarSerializer

class CalendarService:

    @staticmethod
    def generate_calendar(user, school_id, student_id, start_date, end_date):
        
        if user.role == 'trainer':
            trainer = TrainerService.get_trainer_by_user(user)
            sessions = SessionService.get_sessions_by_trainer_school_and_date_in_range(trainer.id, school_id, start_date, end_date)
        elif user.role in ['coordinator', 'admin']:
            if student_id:
                sessions = SessionService.get_sessions_by_student_and_date_in_range(student_id, school_id, start_date, end_date)
            else:
                sessions = SessionService.get_sessions_by_school_and_date_in_range(school_id, start_date, end_date)
        elif user.role == 'student':
            if not student_id:
                return {"error": "student_id  is needed for parents"}
            parent = StudentService.get_parent_by_user(user)
            student = get_object_or_404(StudentService.get_students_by_parent(parent), pk=student_id)
            sessions = SessionService.get_sessions_by_student_and_date_in_range(student.id, school_id, start_date, end_date)
        else:
            sessions = Session.objects.none()

        sessions_by_date = {}
        for session in sessions:
            date_str = session.date.strftime('%d-%m-%Y')
            if date_str not in sessions_by_date:
                sessions_by_date[date_str] = []
            sessions_by_date[date_str].append(session)

        days_off = SchoolService.get_days_off_in_range(start_date, end_date)
        days_off_dates = set()
        for day_off in days_off:
            number_of_days_off = (day_off.last_day_off - day_off.first_day_off).days + 1
            for day_no in range(number_of_days_off):
                days_off_dates.add((day_off.first_day_off + timedelta(day_no)).strftime('%d-%m-%Y'))

        calendar = {}
        for single_date in (start_date + timedelta(n) for n in range(30)):
            date_str = single_date.strftime('%d-%m-%Y')
            if date_str in days_off_dates:
                calendar[date_str] = {
                    "courses": {},
                    "status": "vacation"
                }
            else:
                if date_str in sessions_by_date:
                    sessions_data = SessionForCalendarSerializer(sessions_by_date[date_str], many=True).data
                    status = "my_course" if user.role in ['student', 'trainer'] else "course"
                    calendar[date_str] = {
                        "courses": sessions_data,
                        "status": status
                    }
                else:
                    calendar[date_str] = {
                        "courses": {},
                        "status": "no_courses"
                    }
        
        return calendar
