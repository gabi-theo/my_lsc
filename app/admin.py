from django.contrib import admin

from .models import (
    AbsentStudent,
    Course,
    CourseDays,
    CourseDescription,
    CourseSchedule,
    MakeUp,
    News,
    School,
    Session,
    SessionsDescription,
    Student,
    StudentCourseSchedule,
    Trainer,
    TrainerSchedule,
    User,
    DaysOff,
    Room,
    TrainerFromSchool,
    Parent,
    DailySchoolSchedule,
    SchoolSchedule,
    Feedback,
)

# Register your models here.
admin.site.register(DailySchoolSchedule)
admin.site.register(SchoolSchedule)
admin.site.register(School)
admin.site.register(Course)
admin.site.register(CourseDescription)
admin.site.register(Student)
admin.site.register(CourseSchedule)
admin.site.register(Trainer)
admin.site.register(TrainerSchedule)
admin.site.register(Session)
admin.site.register(SessionsDescription)
admin.site.register(CourseDays)
admin.site.register(MakeUp)
admin.site.register(News)
admin.site.register(User)
admin.site.register(StudentCourseSchedule)
admin.site.register(DaysOff)
admin.site.register(AbsentStudent)
admin.site.register(Room)
admin.site.register(TrainerFromSchool)
admin.site.register(Parent)
admin.site.register(Feedback)
