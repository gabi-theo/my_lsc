from app.models import (
    User,
    Room,
    School,
    Course,
    CourseDays,
    SchoolSchedule,
    DailySchoolSchedule,
    Trainer,
    TrainerSchedule,
)

from app.services.users import UserService
from app.services.dailyschoolschedule import DailySchoolScheduleService
from my_lsc.settings import DEBUG

from datetime import (
    datetime,
    timedelta
)

from json import load

from schema import (
    Schema,
    And,
    Or,
    Use,
    Optional,
)

from re import match

START_DATE = datetime(2024, 2, 1) if DEBUG else datetime.now()


def make_up_dates(start_date):
    date = start_date
    for _ in range(DailySchoolScheduleService.MAKE_UP_LOOKAHEAD_DAYS):
        yield date
        date += timedelta(days=1)


def get_room_by_name(name: str):
    return Room.objects.filter(room_name=name).first()


def get_school_by_name(name: str):
    return School.objects.filter(name=name).first()


def load_data_from_file(file_path) -> tuple[bool, dict]:
    with open(file_path, encoding="utf-8") as file:
        file_data: dict = load(file)

        valid_data = is_valid_input_data_format(input_data=file_data)

        if not valid_data:
            return False, {}

        result = {}

        result["admin"] = User.objects.create(
            username="admin", password="admin")

        result["users"] = [
            User.objects.create(
                username=data["username"],
                password=data["password"]
            )
            for data in file_data["users"]
        ]

        result["schools"] = [
            School.objects.create(
                name=data["name"],
                phone_contact=data["phone_contact"],
                email_contact=data["email_contact"],
                user=UserService.get_user_by_username(data["user_username"])
            )
            for data in file_data["schools"]
        ]

        result["rooms"] = [
            Room.objects.create(
                room_name=data["name"],
                capacity=data["capacity"],
                school=get_school_by_name(data["school_name"])
            )
            for data in file_data["rooms"]
        ]

        result["course_days"] = [
            CourseDays.objects.create(day=course_day)
            for course_day in file_data["course_days"]
        ]

        result["school_schedules"] = [
            SchoolSchedule.objects.create(
                school=get_school_by_name(data["school_name"]),
                working_day=data["working_day"],
                start_hour=datetime.strptime(
                    data["start_hour"], "%H:%M:%S").time(),
                end_hour=datetime.strptime(
                    data["end_hour"], "%H:%M:%S").time()
            )
            for data in file_data["school_schedules"]
        ]

        result["trainers"] = [
            Trainer.objects.create(
                first_name=data["first_name"],
                last_name=data["last_name"],
                phone_contact=data["phone_contact"],
                email_contact=data["email_contact"],
                user=UserService.get_user_by_username(data["user_username"])
            )
            for data in file_data["trainers"]
        ]

        result["trainer_schedules"] = {
            trainer_idx: TrainerSchedule.objects.create(
                date=datetime.strptime(data["date"], "%Y-%m-%d").date(),
                trainer=result["trainers"][data["trainer_idx"]],
                available_day=CourseDays.objects.filter(day=data["available_day"]).first(),
                available_hour_from=datetime.strptime(
                    data["available_hour_from"], "%H:%M:%S").time(),
                available_hour_to=datetime.strptime(
                    data["available_hour_to"], "%H:%M:%S").time(),
                school=get_school_by_name(data["school_name"])
            )
            for trainer_idx, data in file_data["trainer_schedules"].items()
        }

        result["daily_school_schedules"] = {
            DailySchoolSchedule.objects.create(
                school_schedule=result["school_schedules"][data["school_schedule_idx"]],
                date=datetime.strptime(data["date"], "%Y-%m-%d").date(),
                busy_from=datetime.strptime(
                    data["busy_from"], "%H:%M:%S").time(),
                busy_to=datetime.strptime(
                    data["busy_to"], "%H:%M:%S").time(),
                blocked_by=data["blocked_by"],
                room=get_room_by_name(data["room_name"]),
                trainer_involved=result["trainers"][data["trainer_involved_idx"]],
                activity_type="sed",
            )
            for data in file_data["daily_school_schedules"]
        }

        result["courses"] = [
            Course.objects.create(course_type=course)
            for course in file_data["courses"]
        ]

        return True, result


def erase_data():
    User.objects.all().delete()
    School.objects.all().delete()
    Room.objects.all().delete()
    CourseDays.objects.all().delete()
    SchoolSchedule.objects.all().delete()
    Trainer.objects.all().delete()
    TrainerSchedule.objects.all().delete()
    DailySchoolSchedule.objects.all().delete()
    Course.objects.all().delete()


def erase_and_load_data(file_path: str) -> tuple[bool, dict]:
    erase_data()
    return load_data_from_file(file_path=file_path)


def is_valid_email(email) -> bool:
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return match(pattern, email) is not None


def is_valid_date(time_str):
    try:
        datetime.strptime(time_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def is_valid_time(time_str):
    try:
        datetime.strptime(time_str, "%H:%M:%S")
        return True
    except ValueError:
        return False


def school_name_exists(input_data: dict):
    def _school_name_exists(school_name) -> bool:
        return school_name in [_["name"] for _ in input_data["schools"]]
    return _school_name_exists


def user_username_exists(input_data: dict):
    def _user_username_exists(user_name) -> bool:
        return user_name in [_["username"] for _ in input_data["users"]]
    return _user_username_exists


def room_name_exists(input_data: dict):
    def _room_name_exists(room_name) -> bool:
        return room_name in [_["name"] for _ in input_data["rooms"]]
    return _room_name_exists


def is_valid_input_data_format(input_data: dict) -> bool:
    good_schema = Schema(
        {
            "users": [
                {
                    "username": str,
                    "password": str,
                }
            ],
            "schools": [
                {
                    "name": str,
                    "phone_contact": str,
                    "email_contact": And(
                        str,
                        is_valid_email,
                    ),
                    "user_username": And(
                        str,
                        user_username_exists(input_data=input_data),
                    ),
                }
            ],
            "rooms": [
                {
                    "name": str,
                    "capacity": And(
                        Use(int),
                        lambda x: x > 0,
                    ),
                    "school_name": And(
                        str,
                        school_name_exists(input_data=input_data),
                    ),
                }
            ],
            "course_days": [
                "luni",
                "marti",
                "miercuri",
                "joi",
                "vineri",
            ],
            "school_schedules": [
                {
                    "school_name": And(
                        str,
                        school_name_exists(input_data=input_data),
                    ),
                    "working_day": Or(
                        "luni",
                        "marti",
                        "miercuri",
                        "joi",
                        "vineri",
                    ),
                    "start_hour": And(
                        str,
                        is_valid_time,
                    ),
                    "end_hour": And(
                        str,
                        is_valid_time,
                    ),
                }
            ],
            "trainers": [
                {
                    "first_name": str,
                    "last_name": str,
                    "phone_contact": str,
                    "email_contact": And(
                        str,
                        is_valid_email,
                    ),
                    "user_username": And(
                        str,
                        user_username_exists(input_data=input_data),
                    ),
                }
            ],
            "trainer_schedules": Or(
                {
                    Use(int): {
                        "trainer_idx": Use(int),
                        "date": And(
                            str,
                            is_valid_date,
                        ),
                        "available_day": Or(
                            "luni",
                            "marti",
                            "miercuri",
                            "joi",
                            "vineri",
                        ),
                        "available_hour_from": And(
                            str,
                            is_valid_time,
                        ),
                        "available_hour_to": And(
                            str,
                            is_valid_time,
                        ),
                        "school_name": And(
                            str,
                            school_name_exists(input_data=input_data),
                        ),
                    }
                },
                {},
            ),
            "daily_school_schedules": [
                {
                    "date": And(
                        str,
                        is_valid_date,
                    ),
                    "busy_from": And(
                        str,
                        is_valid_time,
                    ),
                    "busy_to": And(
                        str,
                        is_valid_time,
                    ),
                    "blocked_by": Or(
                        "course",
                        "make_up",
                        "other",
                    ),
                    "room_name": And(
                        str,
                        room_name_exists(input_data=input_data),
                    ),
                    "trainer_involved_idx": And(
                        Use(int),
                        lambda x: x >= 0,
                    ),
                    "school_schedule_idx": And(
                        Use(int),
                        lambda x: x >= 0,
                    ),
                },
            ],
            Optional("courses"): [
                "Unity",
            ]
        }
    )

    # print(good_schema.validate(data=input_data))

    return good_schema.is_valid(data=input_data)


def is_valid_response_format(response_json: dict) -> bool:
    good_schema = Schema(
        {
            Or(
                "sed",
                "onl",
            ):
            {
                And(
                    str,
                    is_valid_date,
                ):
                Or(
                    {
                        str:
                        {
                            "busy":
                            [
                                {
                                    "start": And(
                                        str,
                                        is_valid_time,
                                    ),
                                    "end": And(
                                        str,
                                        is_valid_time,
                                    ),
                                    "type": Or(
                                        "course",
                                        "make_up",
                                        "other",
                                    ),
                                },
                            ],
                            "free": [
                                {
                                    "start": And(
                                        str,
                                        is_valid_time,
                                    ),
                                    "end": And(
                                        str,
                                        is_valid_time,
                                    ),
                                },
                            ],
                            "schedule": And(
                                str,
                                lambda x: all(
                                    is_valid_time(t.strip())
                                    for t in x.split("-")
                                ),
                            ),
                        },
                    },
                    {},
                ),
            },
        }
    )

    return good_schema.is_valid(data=response_json)
