from app.models import (
    DaysOff,
    Room,
)


class SchoolService:
    @staticmethod
    def get_days_off_for_school(school):
        return DaysOff.objects.filter(school=school)

    @staticmethod
    def get_rooms_by_school(school):
        return Room.objects.filter(school=school)
    
    @staticmethod
    def get_days_off_in_range(start_date, end_date):
        return DaysOff.objects.filter(first_day_off__lte=end_date, last_day_off__gte=start_date)
