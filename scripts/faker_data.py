import uuid
import random
from faker import Faker
from datetime import datetime, timedelta
from django.contrib.auth import get_user_model
from app.models import (
    School, Room, DaysOff, CourseDays, Course, Trainer, TrainerFromSchool,
    Parent, Student, CourseSchedule, StudentCourseSchedule, TrainerSchedule,
    Session, SessionPresence, MakeUp, AbsentStudent, CourseDescription,
    SessionsDescription, SentWhatsappMessages, SentEmailsMessages,
    StudentInvoice, Invoice
)

fake = Faker()
User = get_user_model()


# Function to create fake data for the models
def generate_fake_data():
    # Create a superuser for testing
    try:
        superuser = User.objects.create_superuser(username='admin', password='admin')
    except Exception as e:
        print(e)

    # Create schools
    schools = []
    for _ in range(3):
        user = User.objects.create_user(role="coordinator", username=f"coordinator{_}", password=f"coordinator{_}")
        school = School.objects.create(
            user=user,
            name=fake.company(),
            phone_contact=fake.phone_number(),
            email_contact=fake.email(),
            smartbill_api_key=fake.uuid4()
        )
        schools.append(school)

    # Create rooms
    rooms = []
    for school in schools:
        for _ in range(5):
            room = Room.objects.create(
                room_name=fake.word(),
                capacity=random.randint(10, 30),
                school=school
            )
            rooms.append(room)

    # Create days off
    for school in schools:
        for _ in range(5):
            DaysOff.objects.create(
                first_day_off=fake.date_between(start_date='-30d', end_date='+30d'),
                last_day_off=fake.date_between(start_date='+31d', end_date='+60d'),
                day_off_info=fake.text(),
                school=school
            )

    # Create course days
    for _ in range(7):
        CourseDays.objects.create(day=random.choice(['luni', 'marti', 'miercuri', 'joi', 'vineri', 'sambata', 'duminica']))

    # Create courses
    courses = []
    for _ in range(5):
        course = Course.objects.create(
            course_type=fake.word()
        )
        courses.append(course)

    # Create trainers
    trainers = []
    for _ in range(5):
        trainer = Trainer.objects.create(
            user=User.objects.create_user(
                username=fake.user_name(),
                password=fake.password(),
            ),
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            phone_contact=fake.phone_number(),
            email_contact=fake.email(),
        )
        trainers.append(trainer)

    # Create trainers from school
    for school in schools:
        for trainer in random.sample(trainers, random.randint(2, 4)):
            TrainerFromSchool.objects.create(school=school, trainer=trainer)

    # Create parents
    parents = []
    for _ in range(5):
        parent = Parent.objects.create(
            user=User.objects.create_user(
                username=fake.user_name(),
                password=fake.password(),
            ),
            school=random.choice(schools),
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            phone_number1=fake.phone_number(),
            phone_number2=fake.phone_number(),
            email1=fake.email(),
            email2=fake.email(),
            active_account=fake.boolean()
        )
        parents.append(parent)

    # Create students
    students = []
    for parent in parents:
        for _ in range(random.randint(1, 3)):
            student = Student.objects.create(
                parent=parent,
                first_name=fake.first_name(),
                last_name=fake.last_name(),
            )
            students.append(student)

    # Create course schedules
    for school in schools:
        for course in courses:
            for _ in range(2):
                course_schedule = CourseSchedule.objects.create(
                    course=course,
                    school=school,
                    group_name=fake.word(),
                    total_sessions=random.randint(5, 10),
                    first_day_of_session=fake.date_between(start_date='-30d', end_date='+30d'),
                    last_day_of_session=fake.date_between(start_date='+31d', end_date='+60d'),
                    day=random.choice(['luni', 'marti', 'miercuri', 'joi', 'vineri', 'sambata', 'duminica']),
                    start_time=fake.time(),
                    end_time=fake.time(),
                    classroom=random.choice(rooms),
                    default_trainer=random.choice(trainers),
                    course_type=random.choice(['onl', 'hbr', 'sed']),
                    online_link=fake.url(),
                    can_be_used_as_online_make_up_for_other_schools=fake.boolean(),
                    available_places_for_make_up_online=random.randint(1, 5),
                    available_places_for_make_up_on_site=random.randint(1, 5),
                )

                for student in random.sample(students, random.randint(5, 8)):
                    StudentCourseSchedule.objects.create(student=student, course_schedule=course_schedule)

    # Create trainer schedules
    for trainer in trainers:
        for _ in range(5):
            TrainerSchedule.objects.create(
                year=fake.year(),
                week=fake.random_int(min=1, max=52),
                date=fake.date_between(start_date='-30d', end_date='+30d'),
                trainer=trainer,
                available_day=random.choice(CourseDays.objects.all()),
                available_hour_from=fake.time(),
                available_hour_to=fake.time(),
                online_only=fake.boolean(),
                is_available=fake.boolean(),
                school=random.choice(schools),
            )

    # Create sessions
    for course_schedule in CourseSchedule.objects.all():
        for session_no in range(1, course_schedule.total_sessions + 1):
            Session.objects.create(
                course_session=course_schedule,
                session_trainer=random.choice(trainers),
                session_passed=fake.boolean(),
                date=fake.date_between_dates(course_schedule.first_day_of_session, course_schedule.last_day_of_session),
                session_no=session_no,
            )

    # Create session presences
    for session in Session.objects.all():
        for student in session.course_session.students.all():
            SessionPresence.objects.create(student=student, session=session, status=random.choice(['present', 'absent', 'made_up']))

    # Create make-ups
    for session_presence in SessionPresence.objects.filter(status='absent'):
        MakeUp.objects.create(
            date_time=fake.date_time_between(start_date=session_presence.session.date, end_date=session_presence.session.date),
            online_link=fake.url(),
            type=random.choice(['onl', 'hbr', 'sed']),
            duration_in_minutes=random.randint(30, 120),
            trainer=random.choice(trainers),
            make_up_approved=fake.boolean(),
            make_up_completed=fake.boolean(),
            can_be_used_as_online_make_up_for_other_schools=fake.boolean(),
            available_places_for_make_up_online=random.randint(1, 5),
            available_places_for_make_up_on_site=random.randint(1, 5),
            session=session_presence.session,
        )

    # Create absent students
    for student in students:
        for absent_session in Session.objects.all():
            absent_course_schedule = absent_session.course_session
            AbsentStudent.objects.create(
                absent_participant=student,
                absent_on_session=absent_session,
                is_absence_in_crm=fake.boolean(),
                is_absence_communicated_to_parent=fake.boolean(),
                is_absence_completed=fake.boolean(),
                is_absent_for_absence=fake.boolean(),
                has_make_up_scheduled=fake.boolean(),
                choosed_course_session_for_absence=absent_session,
                choosed_make_up_session_for_absence=MakeUp.objects.filter(session=absent_session).first(),
                is_make_up_online=fake.boolean(),
                is_make_up_on_site=fake.boolean(),
                comment=fake.text(),
            )

    # Create course descriptions
    for course in courses:
        CourseDescription.objects.create(
            course=course,
            short_description=fake.text(max_nb_chars=100),
            long_description=fake.text(max_nb_chars=1000),
        )

    # Create session descriptions
    for course in courses:
        SessionsDescription.objects.create(
            course=course,
            min_session_no_description=fake.random_int(min=1, max=5),
            max_session_no_description=fake.random_int(min=6, max=10),
            description=fake.text(max_nb_chars=1000),
        )

    # Create WhatsApp messages
    for _ in range(5):
        SentWhatsappMessages.objects.create(
            sent_on_time=fake.time(),
            sent_on_date=fake.date_between(start_date='-30d', end_date='+30d'),
            sent_to_number=fake.phone_number(),
            sent_message=fake.text(max_nb_chars=500),
            has_errors=fake.boolean(),
            error_message=fake.text(max_nb_chars=500),
        )

    # Create Email messages
    for _ in range(5):
        SentEmailsMessages.objects.create(
            sent_on_time=fake.time(),
            sent_on_date=fake.date_between(start_date='-30d', end_date='+30d'),
            sent_to_mail=fake.email(),
            sent_mail_subject=fake.text(max_nb_chars=500),
            sent_mail_body=fake.text(max_nb_chars=500),
            has_errors=fake.boolean(),
            error_message=fake.text(max_nb_chars=500),
        )

    # Create student invoices
    for student in students:
        for course_schedule in StudentCourseSchedule.objects.filter(student=student):
            StudentInvoice.objects.create(
                student=student,
                course_schedule=course_schedule.course_schedule,
                payment_frequency=random.choice(['monthly', 'module', 'yearly', 'four_courses']),
                module_full_price=fake.random_int(min=100, max=500),
                invoice_price=fake.random_int(min=50, max=300),
                full_discount=fake.random_int(min=0, max=50),
                discount_details=fake.text(max_nb_chars=100),
                invoice_with_student_found=fake.boolean(),
                smartbill_client=fake.uuid4(),
                smarbill_cif=fake.uuid4(),
                smarbill_email=fake.email(),
                smarbill_phone=fake.phone_number(),
            )

    # Create invoices
    for student_invoice in StudentInvoice.objects.all():
        Invoice.objects.create(
            student_invoice=student_invoice,
            invoice_no=fake.uuid4(),
            invoice_status=random.choice(['platita', 'emisa', 'depasita', 'anulata']),
            invoice_date_time=fake.date_time_between(start_date=student_invoice.course_schedule.first_day_of_session, end_date=student_invoice.course_schedule.last_day_of_session),
        )


def erase_and_create_fake_data():
    # Delete existing data
    SessionPresence.objects.all().delete()
    AbsentStudent.objects.all().delete()
    MakeUp.objects.all().delete()
    Session.objects.all().delete()
    TrainerSchedule.objects.all().delete()
    StudentCourseSchedule.objects.all().delete()
    CourseSchedule.objects.all().delete()
    StudentInvoice.objects.all().delete()
    Invoice.objects.all().delete()
    SentEmailsMessages.objects.all().delete()
    SentWhatsappMessages.objects.all().delete()
    SessionsDescription.objects.all().delete()
    CourseDescription.objects.all().delete()
    Course.objects.all().delete()
    TrainerFromSchool.objects.all().delete()
    Trainer.objects.all().delete()
    User.objects.all().delete()
    Parent.objects.all().delete()
    Student.objects.all().delete()
    Room.objects.all().delete()
    School.objects.all().delete()
    DaysOff.objects.all().delete()
    CourseDays.objects.all().delete()
    generate_fake_data()

erase_and_create_fake_data()
