from datetime import datetime, timedelta, time
import secrets
import string
from django.db import models
from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import SlidingToken, UntypedToken
from rest_framework_simplejwt.exceptions import TokenError


def set_value_to_cookie(response, key, value, expires=settings.SESSION_COOKIE_AGE):
    response.set_cookie(
        key=key,
        value=value,
        expires=expires,
        httponly=True,
    )


def set_token_to_header(response, token):
    response.headers["x-token"] = token


def check_excel_format_in_request_data(request):
    if 'file' not in request.data:
        return Response({'error': 'File not provided'}, status=status.HTTP_400_BAD_REQUEST)

    excel_file = request.data['file']
    if not excel_file.name.endswith('.xls') and not excel_file.name.endswith('.xlsx'):
        return Response(
            {'error': 'Invalid file format. Please provide an Excel file.'},
            status=status.HTTP_400_BAD_REQUEST,
        )


def format_whised_make_up_times(
    wished_make_up_date,
    wished_make_up_min_time,
    wished_make_up_max_time,
):
    return (
        datetime.strptime(wished_make_up_date, "%Y-%m-%d").date(),
        datetime.strptime(wished_make_up_min_time, "%H:%M:%S").time(),
        datetime.strptime(wished_make_up_max_time, "%H:%M:%S").time(),
    )


def map_to_bool(value):
    if value == "TRUE":
        return True
    elif value == "FALSE" or value == "0":
        return False
    elif value == "1":
        return True
    else:
        return None


def random_password_generator():
    return ''.join(
        secrets.choice(
            string.ascii_letters + string.digits + string.punctuation
        ) for _ in range(12))


def find_available_times(start_time, end_time, busy_intervals):
    start_datetime = datetime.combine(datetime.today().date(), start_time)
    end_datetime = datetime.combine(datetime.today().date(), end_time)

    busy_intervals.sort(key=lambda interval: interval['start'])

    free_intervals = []

    current_datetime = start_datetime

    for interval in busy_intervals:
        interval_end =  interval['end']
        interval_start = interval['start']
        if isinstance(interval['start'], time):
            interval_start = datetime.combine(datetime.today().date(), interval['start'])
        if isinstance(interval['end'], time):
            interval_end = datetime.combine(datetime.today().date(), interval['end'])

        if current_datetime < interval_start:
            free_end = min(interval_start, end_datetime)
            free_intervals.append({
                'start': current_datetime.time(),
                'end': free_end.time(),
            })

        current_datetime = max(current_datetime, interval_end)

    if current_datetime < end_datetime:
        free_intervals.append({
            'start': current_datetime.time(),
            'end': end_datetime.time(),
        })

    return free_intervals


def get_date_of_day_in_same_week(date_str, day_str):
    given_date = datetime.strptime(date_str, "%Y-%m-%d")
    days_to_add = 0
    week_day_number = given_date.weekday()
    week_number = given_date.isocalendar()
    days_of_week = ["luni", "marti", "miercuri", "joi", "vineri", "sambata", "duminica"]
    given_day_index = days_of_week.index(day_str.lower())
    if week_day_number == week_number:
        return given_date
    days_to_add = week_day_number - given_day_index
    return given_date - timedelta(days=days_to_add)

def create_serialized_response_from_object(object, fields):
    serialized_data = {}
    for field_name in fields:
        current_value = object
        for part in field_name.split('__'):
            if part == "trainer" or part == "session_trainer":
                current_value = object.__str__()
            if isinstance(current_value, models.Model):
                current_value = getattr(current_value, part, None)
            else:
                current_value = None
                break
        serialized_data[field_name] = current_value
    return serialized_data
