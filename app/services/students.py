import pandas as pd
from django.db.models import Q
from unidecode import unidecode
from django.shortcuts import get_object_or_404

from app.models import (
    Parent,
    Student,
)
from app.services.courses import CourseService
from core.tasks import send_students_email

class StudentService:
    @staticmethod
    def get_student_by_id(student_id):
        return Student.objects.filter(id=student_id).first()

    @staticmethod
    def get_emails_from_all_active_students():
        return list(
            Student.objects.filter(
                student_active=True
            ).values_list('parent_email', flat=True).distinct())

    @classmethod
    def send_emails_to_students_in_groups(cls, groups:str, subject:str, message:str):
        groups_pks = groups.split(",")
        student_emails = []
        if len(groups_pks) == 1 and groups_pks[0] == "all":
            student_emails = cls.get_emails_from_all_active_students()
        else:
            student_emails = CourseService.get_emails_of_students_from_course_schedule_by_schedule_pks(
                        groups_pks)
        send_students_email.delay(
            student_emails,
            subject,
            message,
        )

    @staticmethod
    def get_students_id_by_phone_or_email(phone, email):
        if phone != "None" and email != "None":
            print(1)
            return Student.objects.filter(
                Q(parent__phone_number1=phone) | Q(parent__phone_number2=phone)
                &
                Q(parent__email1=email) | Q(parent__email2=email))
        elif phone != "None":
            print(2)
            return Student.objects.filter(
                Q(parent__phone_number1=phone) | Q(parent__phone_number2=phone))
        print(3)
        return Student.objects.filter(
                Q(parent__email1=email) | Q(parent__email2=email))

    @staticmethod
    def create_student_from_excel_and_assign_it_to_school_course(
        excel_file,
        school,
    ):
        df = pd.read_excel(excel_file, skiprows=[0])
        for _, row in df.iterrows():
            if isinstance(row["companion_phones"],float):
                row["companion_phones"] = "Missing"
            if isinstance(row["companion_fullName"],float):
                row["companion_fullName"] = "Missing"
            if isinstance(row["companion_emails"],float):
                row["companion_emails"] = "Missing"
            parent, _ = Parent.objects.get_or_create(
                school=school,
                first_name=row["companion_fullName"].split(" ")[0],
                last_name=" ".join(row["companion_fullName"].split(" ")[1:]),
                phone_number1=row["companion_phones"].split(", ")[0],
                phone_number2=" ".join(row["companion_phones"].split(", ")[1:]),
                email1=row["companion_emails"].split(", ")[0],
                email2=" ".join(row["companion_emails"].split(", ")[1:]),
            )
            student, _ = Student.objects.get_or_create(
                parent=parent,
                first_name=row["participant_fullName"].split(" ")[0],
                last_name=" ".join(row["participant_fullName"].split(" ")[1:]),
            )
            discount = float(row["totalDiscountsPct"])
            billing_frequency = row["price.billingPeriod"]
            price_after_discount = float(row["reducedPrice.value"])
            price_before_discount = float(row["price.value"])
            course_schedule = CourseService.add_student_to_course_schedule_by_group_name_day_and_time(
                student=student,
                group_name=row["group_name"],
                day=unidecode(row['schedule_times'].split(" ")[0]),
                time=row['schedule_times'].split(" ")[1],
            )
    
    @staticmethod
    def get_parent_by_user_or_404(user):
        try:
            return Parent.objects.get(user=user)
        except Parent.DoesNotExist:
            return Response({'detail': 'Parent not found'}, status=status.HTTP_404_NOT_FOUND)
    
    @staticmethod
    def get_student_by_parent_and_school(parent, school_id, student_id):
        return Student.objects.filter(parent=parent).first()


    @staticmethod
    def get_student_by_parent1(student_id):
        try:
            return Student.objects.filter(pk=student_id)
        except Student.DoesNotExist:
            return Response({'detail': 'Student not found'}, status=status.HTTP_404_NOT_FOUND)
        
    
    @staticmethod
    def get_parent_by_user(user):
        
        return get_object_or_404(Parent, user=user)
    
    @staticmethod
    def get_students_by_parent(parent):
       
        return Student.objects.filter(parent=parent)