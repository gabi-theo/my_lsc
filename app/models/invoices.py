from uuid import uuid4
from datetime import datetime

from django.db import models


class StudentInvoice(models.Model):
    PAYMENT_TYPE = (
        ("monthly", "Lunar"),
        ("module", "Semestrial"),
        ("yearly", "Anual"),
        ("four_courses", "La 4 cursuri"),
    )

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    student = models.ForeignKey("app.Student", on_delete=models.SET_NULL, null=True, blank=True)
    course_schedule = models.ForeignKey("app.CourseSchedule", on_delete=models.SET_NULL, null=True, blank=True)
    payment_frequency = models.CharField(max_length=50, choices=PAYMENT_TYPE)
    module_full_price = models.FloatField()
    invoice_price = models.FloatField()
    full_discount = models.FloatField()
    discount_details = models.CharField(max_length=100)
    invoice_with_student_found = models.BooleanField(default=False)
    smartbill_client = models.CharField(max_length=100, null=True)
    smarbill_cif = models.CharField(max_length=100, null=True)
    smarbill_email = models.CharField(max_length=100, null=True)
    smarbill_phone = models.CharField(max_length=100, blank=True)


class Invoice(models.Model):
    INVOICE_STATUS = (
        ('platita', 'Platita'),
        ('emisa', 'Emisa'),
        ('depasita', 'Depasita'),
        ('anulata', 'Anulata')
    )
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    student_invoice = models.ForeignKey("app.StudentInvoice", on_delete=models.CASCADE)
    invoice_no = models.CharField(max_length=50)
    invoice_status = models.CharField(max_length=20, choices=INVOICE_STATUS, null=True, blank=True)
    invoice_date_time = models.DateTimeField(default=datetime.now())
