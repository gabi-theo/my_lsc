

import uuid
import random
from time import sleep
from faker import Faker
from datetime import datetime, timedelta, time
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import get_user_model
from app.models import (
    DailySchoolSchedule, School, Room, DaysOff, CourseDays, Course, SchoolSchedule, Trainer, TrainerFromSchool,
    Parent, Student, CourseSchedule, StudentCourseSchedule, TrainerSchedule,
    Session, SessionPresence, MakeUp, AbsentStudent, CourseDescription,
    SessionsDescription, SentWhatsappMessages, SentEmailsMessages,
    StudentInvoice, Invoice
)
n = 0
fake = Faker()
User = get_user_model()


def random_date(start_datetime: datetime, end_datetime: datetime, start_hour=14, end_hour=19):
    # Generate a random date within the interval
    delta_days = (end_datetime - start_datetime).days
    random_days = random.randint(0, delta_days)
    random_date = start_datetime + timedelta(days=random_days)

    # Generate a random time between 14:00 and 19:00 with minutes divisible by 15
    random_hour = random.randint(start_hour, end_hour)
    random_minute = random.choice([0, 15, 30, 45])

    # Combine random date and time
    random_date_time = datetime(
        random_date.year, 
        random_date.month, 
        random_date.day, 
        random_hour, 
        random_minute
    )
    return random_date_time

def random_time(start_hour, end_hour):
    sleep(0.1)
    # Generate random hour
    hour = random.randint(start_hour, end_hour)
    
    # Generate random minute (either 0 or 30)
    minute = random.choice([0, 30])
    
    # Get current date
    current_date = datetime.now().date()
    
    # Construct datetime object with random hour and minute
    random_datetime = datetime.combine(current_date, datetime.min.time()) + timedelta(hours=hour, minutes=minute)
    
    return random_datetime.time()


# Function to create fake data for the models
def generate_fake_data():
    print("GENERATING FAKE DATA.........")
    # Create a superuser for testing
    print("__________")
    print("CREATING SUPER USER")
    try:
        superuser = User.objects.create_superuser(username='admin', password='admin')
    except Exception as e:
        print(e)
    print("DONE CREATING SUPER USER")
    # Create schools
    schools = []
    print("__________")
    print("CREATING SCHOOLS AND COORDINATORS")
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
    print("DONE CREATING SCHOOLS")
    print("__________")
    # Create rooms
    rooms = []
    print("POPULATING ROOMS")
    for school in schools:
        for _ in range(5):
            room = Room.objects.create(
                room_name=fake.word(),
                capacity=random.randint(10, 30),
                school=school
            )
            rooms.append(room)
    print("DONE POPULATING ROOMS")
    print("__________")
    # Create days off
    print("CREATING DAYS OFF")
    for school in schools:
        for _ in range(5):
            DaysOff.objects.create(
                first_day_off=fake.date_between(start_date='-30d', end_date='+30d'),
                last_day_off=fake.date_between(start_date='+31d', end_date='+60d'),
                day_off_info=fake.text(),
                school=school
            )
    print("DONE CREATING DAYS OFF")
    print("__________")
    print("CREATING COURSE DAYS")
    # Create course days
    for day in ['luni', 'marti', 'miercuri', 'joi', 'vineri', 'sambata', 'duminica']:
        CourseDays.objects.create(day=day)
    print("DONE CREATING COURSE DAYS")
    print("__________")
    # Create courses
    print("CREATING COURSES")

    courses = []
    for _ in range(5):
        course = Course.objects.create(
            course_type=fake.word()
        )
        courses.append(course)

    print("DONE CREATING COURSES")
    print("__________")

    # Create trainers
    trainers = []
    print("CREATING TRAINERS")
    for _ in range(20):
        user = User.objects.create_user(role="trainer", username=f"trainer{_}", password=f"trainer{_}")
        trainer = Trainer.objects.create(
            user=user,
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            phone_contact=fake.phone_number(),
            email_contact=fake.email(),
        )
        trainers.append(trainer)

    print(f"Total trainers created: {len(trainers)}")
    print("DONE CREATING TRAINERS")
    print("__________")
    # Create trainers from school
    print("ADDING TRAINERS TO SCHOOLS AND CREATING DEFAULT TRAINER SCHEDULE (default each day from 09:00 to 21:00)")
    for school in schools:
        for trainer in random.sample(trainers, random.randint(4, 7)):
            TrainerFromSchool.objects.create(school=school, trainer=trainer)

            # Create trainer schedules
            start_date = datetime(2024, 1, 1)
            end_date = datetime(2024, 6, 30)
            dates = [start_date + timedelta(days=i) for i in range((end_date - start_date).days + 1)]
            for date in dates:
                TrainerSchedule.objects.create(
                    year=2024,
                    week=date.isocalendar().week,
                    date=datetime(year=2024,month=date.month,day=date.day),
                    trainer=trainer,
                    available_day=random.choice(CourseDays.objects.all()),
                    available_hour_from=datetime(year=2024,month=date.month,day=1, hour=9, minute=0).time(),
                    available_hour_to=datetime(year=2024,month=date.month,day=1, hour=21, minute=0).time(),
                    online_only=fake.boolean(),
                    school=school,
                )
    print("DONE ADDING TRAINERS TO SCHOOLS")
    print("__________")
    # Create parents
    print("CREATING PARENTS AND USERS FOR PARENTS")
    parents = []
    for i in range(random.randint(50,100)):
        username = fake.user_name()
        password = fake.password()
        exists = True
        if i == 1:
            username = "stud1"
            password = "stud1"
        user = User.objects.filter(username=username, password=password)
        while user.exists():
            username = fake.user_name()
            password = fake.password()
            user = User.objects.filter(username=username, password=password)
        
        parent = Parent.objects.create(
            user=User.objects.create_user(
                            username=username,
                            password=password,
                            role="student",
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
    print(f"Total parents created: {len(parents)}")
    print("DONE CREATING PARENTS")
    print("__________")
    print("CREATING STUDENTS AND ASSIGNING BETWEEN 1 AND 3 KIDS TO PARENTS")
    # Create students
    students = []
    for parent in parents:
        for i in range(random.randint(1, 3)):
            student = Student.objects.create(
                parent=parent,
                first_name=fake.first_name(),
                last_name=fake.last_name(),
            )
            students.append(student)
    print(f"Total students created: {len(students)}")
    print("DONE CREATING STUDENTS")
    print("__________")
    # Create course schedules
    print("CREATING GROUPS/COURSESCHEDULES, ASSIGING STUDENTS TO EACH COURSE")
    course_schedules = []
    for school in schools:
        trainers_from_school = TrainerFromSchool.objects.filter(school=school).order_by("?").first()
        for course in courses:
            for _ in range(2):
                course_type = random.choice(['onl', 'hbr', 'sed'])
                start_time = random_time(14, 19)
                course_schedule = CourseSchedule.objects.create(
                    course=course,
                    school=school,
                    group_name=fake.word(),
                    total_sessions=random.randint(15, 18),
                    # first_day_of_session=fake.date_between(start_date='-30d', end_date='+30d'),
                    # last_day_of_session=fake.date_between(start_date='+31d', end_date='+60d'),
                    first_day_of_session=datetime(year=2024, month=1, day=15),
                    last_day_of_session=datetime(year=2024, month=6, day=30),
                    day=random.choice(['luni', 'marti', 'miercuri', 'joi', 'vineri', 'sambata', 'duminica']),
                    start_time=start_time,
                    end_time=(datetime.combine(datetime.today(), start_time) + timedelta(0,90*60)).time(),
                    default_trainer=trainers_from_school.trainer,
                    course_type=course_type,
                    classroom=random.choice(rooms) if course_type in ["hbr", "sed"] else None,
                    online_link=fake.url(),
                    can_be_used_as_online_make_up_for_other_schools=fake.boolean(),
                    available_places_for_make_up_online=random.randint(1, 5),
                    available_places_for_make_up_on_site=random.randint(1, 5),
                )
                course_schedules.append(course_schedule)
    for student in students:
        courses1 = random.sample(course_schedules, random.randint(1, 2))
        for course in courses1:
            StudentCourseSchedule.objects.create(student=student, course_schedule=course)
    print("DONE CREATING GROUPS/COURSESCHEDULES")
    print("__________")

    # Create session presences
    print("CREATING RANDOM PRESENCE STATUS FOR EACH SESSION AND EACH STUDENT")
    absent_students = []
    for session in Session.objects.all():
        for student in session.course_session.students.all():
            status=random.choice(['present', 'absent', 'made_up'])
            if status != "present":
                absent_students.append((student, session, status))
            SessionPresence.objects.create(student=student, session=session, status=status)
    print(f"Total absent students: {len(absent_students)}")
    print("DONE CREATING PRESENCE")
    print("__________")

    # Create make-ups
    print("CREATE ABSENT STUDENTS AND ASSIGN TO MAKEUPS. NOT ALL ABSENT STUDENTS WILL HAVE A MAKEUP")
    # Create absent students
    for student in absent_students:
        absent_course_schedule = student[1].course_session
        should_create_make_up = random.randint(0, 1)
        makeup = None
        if should_create_make_up and student[2] == "absent":
            mu_type = random.choice(['onl', 'hbr', 'sed'])
            makeup = MakeUp.objects.create(
                date_time=random_date(datetime(2024,1,15, 14, 0), datetime(2024,6,30, 20, 0)),
                online_link=fake.url(),
                type=mu_type,
                duration_in_minutes=30,
                trainer=random.choice(trainers),
                make_up_approved=fake.boolean(),
                make_up_completed=False,
                classroom=random.choice(rooms) if mu_type in ["hbr", "sed"] else None,
                can_be_used_as_online_make_up_for_other_schools=fake.boolean(),
                available_places_for_make_up_online=random.randint(1, 5),
                available_places_for_make_up_on_site=random.randint(1, 5),
                session=student[1],
            )
        elif student[2] == "made_up":
            mu_type = random.choice(['onl', 'hbr', 'sed'])

            makeup = MakeUp.objects.create(
                date_time=random_date(datetime(2024,3,1, 14, 0), datetime(2024,7,30, 20, 0)),
                online_link=fake.url(),
                type=mu_type,
                duration_in_minutes=30,
                trainer=random.choice(trainers),
                make_up_approved=fake.boolean(),
                make_up_completed=True,
                classroom=random.choice(rooms) if mu_type in ["hbr", "sed"] else None,
                can_be_used_as_online_make_up_for_other_schools=fake.boolean(),
                available_places_for_make_up_online=random.randint(1, 5),
                available_places_for_make_up_on_site=random.randint(1, 5),
                session=student[1],
            )
        AbsentStudent.objects.create(
            absent_participant=student[0],
            absent_on_session=student[1],
            is_absence_in_crm=fake.boolean(),
            is_absence_communicated_to_parent=fake.boolean(),
            is_absence_completed=True if student[2] == "made_up" else False,
            is_absent_for_absence=fake.boolean(),
            has_make_up_scheduled=True if makeup else False,
            choosed_course_session_for_absence=student[1],
            choosed_make_up_session_for_absence=MakeUp.objects.filter(session=student[1]).first(),
            is_make_up_online=fake.boolean(),
            is_make_up_on_site=fake.boolean(),
            comment=fake.text(),
        )
    print("DONE CREATING ABSENT STUDENTS AND MAKEUPS")
    print("__________")
    print("GENERATING THE REST OF THE FAKE DATA")

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
    print("DONE GENERATING FAKE DATA")

def erase_and_create_fake_data():
    print("REMOVING ALL EXISTING DATA!!!")
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
    print("DONE REMOVING ALL DATA")
    generate_fake_data()

erase_and_create_fake_data()
