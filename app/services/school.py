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