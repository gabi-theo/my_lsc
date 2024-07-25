from django.db.models import Q
from app.models import (
    Parent,
    )

class RegisterService:
    
    @staticmethod
    def find_parent_by_contact(phone_number, email):
        return Parent.objects.filter(
            (Q(phone_number1=phone_number) & Q(email1=email)) |
            (Q(phone_number1=phone_number) & Q(email2=email)) |
            (Q(phone_number2=phone_number) & Q(email1=email)) |
            (Q(phone_number2=phone_number) & Q(email2=email))
        ).first()

    @staticmethod
    def find_parent_by_phone(phone_number):
        return Parent.objects.filter(
            Q(phone_number1=phone_number) | Q(phone_number2=phone_number)
        ).first()

    @staticmethod
    def find_parent_by_email(email):
        return Parent.objects.filter(
            Q(email1=email) | Q(email2=email)
        ).first()