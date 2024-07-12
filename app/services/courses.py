from datetime import (
    datetime,
    timedelta
)

import pandas as pd
from unidecode import unidecode

from app.models import (
    Course,
    CourseSchedule,
)

from app.utils import map_to_bool


class CourseService:
    @staticmethod
    def get_all_course_schedules():
        return CourseSchedule.objects.all()

    @staticmethod
    def get_courses_from_school(school):
        return CourseSchedule.objects.filter(school=school)

    @staticmethod
    def get_course_schedule_by_pk(pk):
        return CourseSchedule.objects.filter(pk=pk).first()

    @staticmethod
    def get_course_schedules_by_pks(pks):
        return CourseSchedule.objects.filter(pk__in=pks)

    @classmethod
    def get_active_students_from_course_schedule_by_course_schedule_pks(cls, course_schedule_pks):
        course_schedules = cls.get_course_schedules_by_pks(
            course_schedule_pks)
        students_list = []
        for course_schedule in course_schedules:
            students_for_schedule = course_schedule.students.filter(
                student_active=True)
            students_list.extend(students_for_schedule)
        return students_list

    @classmethod
    def get_emails_of_students_from_course_schedule_by_schedule_pks(cls, course_schedule_pks):
        all_students = cls.get_active_students_from_course_schedule_by_course_schedule_pks(
            course_schedule_pks)
        return list(set([stud.parent_email for stud in all_students]))

    @staticmethod
    def create_course_and_course_schedule_from_excel_by_school(
        excel_file,
        school,
    ):
        # Read the Excel file
        df = pd.read_excel(excel_file, skiprows=[0])
        count_courses = 0
        # Loop through the rows and create CourseSchedule objects
        for _, row in df.iterrows():
            if row['totalParticipants'] > 0:
                course, _ = Course.objects.get_or_create(
                    course_type=row['courseType_name'])
                CourseSchedule.objects.create(
                    course=course,
                    group_name=row['name'],
                    total_sessions=row['totalSessions'],
                    first_day_of_session=row['firstDay'],
                    last_day_of_session=row['lastDay'],
                    day=unidecode(row['schedule_times'].split(" ")[0]),
                    start_time=row['schedule_times'].split(" ")[1],
                    course_type="onl" if map_to_bool(row["online"]) else "sed",
                    school=school,
                )
                count_courses += 1
        return count_courses

    @classmethod
    def add_student_to_course_schedule_by_group_name_day_and_time(
        cls,
        student,
        group_name,
        day,
        time,
    ):
        course_schedule = cls.get_course_schedule_by_group_name_day_and_time(
            group_name, day, time,
        )
        course_schedule.students.add(student)
        return course_schedule

    @staticmethod
    def get_course_schedule_by_group_name_day_and_time(
        group_name,
        day,
        time,
    ):
        try:
            return CourseSchedule.objects.get(
                group_name=group_name,
                day=day,
                start_time=time)
        except Exception as e:
            print(
                f"Error for group_name{group_name} on day {day} and time {time}: {e}")
            pass

<<<<<<< HEAD
    @staticmethod
    def get_course_by_id(course_id):
        return Course.objects.get(pk=course_id)
=======
<<<<<<< HEAD
=======
    @staticmethod
    def get_course_by_id(course_id):
        return Course.objects.get(pk=course_id)
>>>>>>> f56d7cc (Finished(?) dailyschoolschedule endpoint)
>>>>>>> 08c1860 (Finished(?) dailyschoolschedule endpoint)
