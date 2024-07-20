from django.db import models


class SentWhatsappMessages(models.Model):
    sent_on_time = models.TimeField(auto_now_add=True)
    sent_on_date = models.DateField(auto_now_add=True)
    sent_to_number = models.CharField(max_length=50)
    sent_message = models.TextField(max_length=500)
    has_errors = models.BooleanField(default=False)
    error_message = models.TextField(null=True, blank=True)


class SentEmailsMessages(models.Model):
    sent_on_time = models.TimeField(auto_now_add=True)
    sent_on_date = models.DateField(auto_now_add=True)
    sent_to_mail = models.CharField(max_length=100)
    sent_mail_subject = models.TextField(max_length=500)
    sent_mail_body = models.TextField(max_length=500)
    has_errors = models.BooleanField(default=False)
    error_message = models.TextField(null=True, blank=True)