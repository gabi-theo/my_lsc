from rest_framework import serializers
from app.services.register import RegisterService
from app.models import (
    User,
)
from django.db import IntegrityError
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.urls import reverse
from django.conf import settings

class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True)
    phone_number = serializers.CharField(write_only=True, max_length=155)
    email = serializers.EmailField(write_only=True)

    def validate(self, attrs):
        phone_number = attrs.get('phone_number')
        email = attrs.get('email')

        parent = RegisterService.find_parent_by_contact(phone_number, email)
        
        if not parent:
            raise serializers.ValidationError("Parent not found with given phone number or email.")
        
        if parent.user:
            raise serializers.ValidationError("Parent already has an user.")
        
        return attrs

    def create(self, validated_data):
        username = validated_data['username']
        password = validated_data['password']
        phone_number = validated_data['phone_number']
        email = validated_data['email']

        parent = RegisterService.find_parent_by_phone(phone_number)
        if not parent:
            parent = RegisterService.find_parent_by_email(email)
        if not parent:
            raise serializers.ValidationError("Parent not found with given phone number and email")
        
        try:
            user = User.objects.create_user(username=username, 
                                        password=password,
                                        is_active=False,
                                        role = 'student')
        except IntegrityError as e:
            raise serializers.ValidationError("User already exists!")
        

        # generate token and email verif
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        parent_id_encoded = urlsafe_base64_encode(force_bytes(parent.pk))
        activation_link = reverse('activate', kwargs={'uidb64': uid, 'token': token, 'parent_id': parent_id_encoded})
        activation_url = f"{settings.SITE_URL}{activation_link}"

        mail_subject = 'Activate your account'
        message = f"Hi {user.username},\n\nPlease click the link below to activate your account:\n\n{activation_url}\n\nThank you!"
        send_mail(mail_subject, message, settings.DEFAULT_FROM_EMAIL, [email])

        return user
