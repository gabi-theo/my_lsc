from rest_framework.response import Response
from rest_framework import generics
from rest_framework import status

from django.db import IntegrityError

from app.serializers import (
    RegisterSerializer,
)


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            user = serializer.save()
        except IntegrityError as e:
            if 'duplicate key value violates unique constraint' in str(e):
                return Response(
                    {"error": "User with this username already exists."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            else:
                return Response(
                    {"error": "Integrity error occurred."},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        return Response({'username': serializer.validated_data['username'], 
                         'email': serializer.validated_data['email'],
                         'phone-number': serializer.validated_data['phone_number']}, 
                         status=status.HTTP_201_CREATED)