from rest_framework import serializers
from app.services.register import RegisterService
from app.models import (
    User,
)
from django.db import IntegrityError


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
                                        role = 'student')
        except IntegrityError as e:
            raise serializers.ValidationError("User already exists!")
        
        parent.user = user
        parent.save()

        return user
