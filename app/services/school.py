from app.models import (
    DaysOff,
    Room,
    School,
    SchoolSchedule,
)

from django.shortcuts import get_object_or_404


class SchoolService:
    @staticmethod
    def get_days_off_for_school(school):
        return DaysOff.objects.filter(school=school)

    @staticmethod
    def get_rooms_by_school(school):
        return Room.objects.filter(school=school)
    
    @staticmethod
    def get_school_by_id(school_id):
        # return get_object_or_404(School, pk=school_id)
        return School.objects.get(pk=school_id)
    
    @staticmethod
    def get_schedules_by_school_and_day(school,day):
        return SchoolSchedule.objects.filter(school=school, working_day=day)