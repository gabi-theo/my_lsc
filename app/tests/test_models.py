from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from app.models import *
from app.services.absences import AbsenceService
from app.services.courses import CourseService
from app.services.makeups import MakeUpService
from app.services.sessions import SessionService
from django.test import TestCase
from datetime import datetime
import unittest
class TestModels(TestCase):

    def test_school_str(self):
        school = School(name="Test School")
        self.assertEqual(str(school), "Test School")
        print("Test 1: se atribuie corect numele scolii")
        
    def test_absent_student_creation(self):
        user = User.objects.create(username="GabiEBossDeBoss", password="FaraParolaCaEPreaBoss")
        school = School.objects.create(name="Test School", phone_contact="123456789", email_contact="test@test.com", user=user)
        room = Room.objects.create(room_name="Room 1", capacity=30, school=school)
        trainer = Trainer.objects.create(first_name="John", last_name="Doe", phone_contact="123456789", email_contact="trainer@test.com", user=user)
        course = Course.objects.create(course_type="Math")

        first_day_of_session = datetime.strptime("2023-06-25", "%Y-%m-%d").date()
        last_day_of_session = datetime.strptime("2023-07-25", "%Y-%m-%d").date()

        course_schedule = CourseSchedule.objects.create(
            course=course,
            school=school,
            group_name="Group A",
            total_sessions=10,
            first_day_of_session=first_day_of_session,
            last_day_of_session=last_day_of_session,
            day="luni",
            start_time="10:00",
            end_time="11:30",
            classroom=room,
            default_trainer=trainer,
            course_type="onl",
        )
        parent = Parent.objects.create(school=school, first_name="John", last_name="Doe")
        student = Student.objects.create(parent=parent, first_name="Jane", last_name="Doe")
        session = Session.objects.create(course_session=course_schedule, date="2023-06-25", session_no=1)
        absent_student = AbsentStudent.objects.create(absent_participant=student, absent_on_session=session)
        self.assertIsInstance(absent_student, AbsentStudent)
        print("Test 2: se atribuie corect elevul absent in clasa AbsentStudent")

    def test_course_creation(self):
        course = Course.objects.create(course_type="Science")
        self.assertEqual(course.course_type, "Science")
        print("Test 3 OK")

    def test_trainer_creation(self):
        user = User.objects.create(username="traineruser", password="password")
        trainer = Trainer.objects.create(first_name="Alice", last_name="Smith", phone_contact="987654321", email_contact="trainer2@test.com", user=user)
        self.assertEqual(trainer.first_name, "Alice")
        self.assertEqual(trainer.last_name, "Smith")
        print("Test 4 OK")

    def test_parent_creation(self):
        user = User.objects.create(username="parentuser", password="password")
        school = School.objects.create(name="Another School", phone_contact="123456789", email_contact="another@test.com", user=user)
        parent = Parent.objects.create(school=school, first_name="James", last_name="Brown")
        self.assertEqual(parent.first_name, "James")
        self.assertEqual(parent.last_name, "Brown")
        print("Test 5 OK")

    def test_student_creation(self):
        user = User.objects.create(username="parentuser2", password="password")
        school = School.objects.create(name="Different School", phone_contact="123456789", email_contact="different@test.com", user=user)
        parent = Parent.objects.create(school=school, first_name="Anna", last_name="Taylor")
        student = Student.objects.create(parent=parent, first_name="Lucy", last_name="Taylor")
        self.assertEqual(student.first_name, "Lucy")
        self.assertEqual(student.last_name, "Taylor")
        print("Test 6 OK")

    def test_room_creation(self):
        user = User.objects.create(username="schooluser", password="password")
        school = School.objects.create(name="Room Test School", phone_contact="123456789", email_contact="room@test.com", user=user)
        room = Room.objects.create(room_name="Room 101", capacity=20, school=school)
        self.assertEqual(room.room_name, "Room 101")
        self.assertEqual(room.capacity, 20)
        print("Test 7 OK")

    def test_course_schedule_creation(self):
        user = User.objects.create(username="scheduleuser", password="password")
        school = School.objects.create(name="Schedule School", phone_contact="123456789", email_contact="schedule@test.com", user=user)
        room = Room.objects.create(room_name="Room 2", capacity=25, school=school)
        trainer = Trainer.objects.create(first_name="Bob", last_name="White", phone_contact="123456789", email_contact="trainer3@test.com", user=user)
        course = Course.objects.create(course_type="History")
        

        first_day_of_session = datetime.strptime("2023-08-01", "%Y-%m-%d").date()
        last_day_of_session = datetime.strptime("2023-09-01", "%Y-%m-%d").date()

        course_schedule = CourseSchedule.objects.create(
            course=course,
            school=school,
            group_name="Group B",
            total_sessions=8,
            first_day_of_session=first_day_of_session,
            last_day_of_session=last_day_of_session,
            day="marti",
            start_time="11:00",
            end_time="12:30",
            classroom=room,
            default_trainer=trainer,
            course_type="off",
        )
        self.assertEqual(course_schedule.group_name, "Group B")
        self.assertEqual(course_schedule.total_sessions, 8)
        print("Test 8 OK")

    def test_session_creation(self):
        user = User.objects.create(username="sessionuser", password="password")
        school = School.objects.create(name="Session School", phone_contact="123456789", email_contact="session@test.com", user=user)
        room = Room.objects.create(room_name="Room 3", capacity=15, school=school)
        trainer = Trainer.objects.create(first_name="Charlie", last_name="Green", phone_contact="123456789", email_contact="trainer4@test.com", user=user)
        course = Course.objects.create(course_type="Geography")

        first_day_of_session = datetime.strptime("2023-10-01", "%Y-%m-%d").date()
        last_day_of_session = datetime.strptime("2023-11-01", "%Y-%m-%d").date()

        course_schedule = CourseSchedule.objects.create(
            course=course,
            school=school,
            group_name="Group C",
            total_sessions=5,
            first_day_of_session=first_day_of_session,
            last_day_of_session=last_day_of_session,
            day="miercuri",
            start_time="12:00",
            end_time="13:30",
            classroom=room,
            default_trainer=trainer,
            course_type="onl",
        )
        
        session = Session.objects.create(course_session=course_schedule, date="2023-10-01", session_no=1)
        session_date = datetime.strptime(session.date, "%Y-%m-%d").date()
        self.assertEqual(session_date, datetime.strptime("2023-10-01", "%Y-%m-%d").date())
        self.assertEqual(session.session_no, 1)
        print("Test 9 OK")

    def test_days_off_creation(self):
        user = User.objects.create(username="daysoffuser", password="password")
        school = School.objects.create(name="Days Off School", phone_contact="123456789", email_contact="daysoff@test.com", user=user)
        
        first_day_off = datetime.strptime("2023-12-24", "%Y-%m-%d").date()
        last_day_off = datetime.strptime("2023-12-26", "%Y-%m-%d").date()

        days_off = DaysOff.objects.create(school=school, first_day_off=first_day_off, last_day_off=last_day_off)
        self.assertEqual(days_off.first_day_off, first_day_off)
        self.assertEqual(days_off.last_day_off, last_day_off)
        print("Test 10 OK")

if __name__ == '__main__':
    unittest.main()

