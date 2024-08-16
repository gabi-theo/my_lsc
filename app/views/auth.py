from rest_framework.generics import GenericAPIView, CreateAPIView
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
)
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK
from rest_framework.views import APIView
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from app.authentication import CookieJWTAuthentication
from app.permissions import (
    IsCoordinator,
    IsTrainer,
)
from app.serializers import (
    SignInSerializer,
    ResetPasswordSerializer,
)
from app.serializers.register import RegisterSerializer
from app.services.users import UserService
from app.services.register import RegisterService

from my_lsc.settings import AUTH_COOKIE_KEY

from django.db import transaction
from django.shortcuts import render, redirect
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.views import View
from app.models.student import Parent

User = get_user_model()

class SignInView(GenericAPIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    serializer_class = SignInSerializer

    def post(self, request: Request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = UserService.get_user_by_username(
            serializer.validated_data["username"])
        user.save()
        response = Response(self.get_serializer(user).data)
        CookieJWTAuthentication.login(user, response)
        return response


class SignOutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(request):
        response = Response({"message": "Bye, see you soon 😌"})
        response.delete_cookie(AUTH_COOKIE_KEY)

        return response


class CheckUserRedirectView(APIView):
    def get(self, request):
        redirect_url = ""
        if request.user.role == "coordinator" and not request.user.user_school.all().exists():
            redirect_url = "http://127.0.0.1:5500/lsc_frontend_simplified/school_create.html"
        elif request.user.role == "parent":
            # TODO: implement
            pass
        else:
            redirect_url = "http://127.0.0.1:5500/lsc_frontend_simplified/today_sessions.html"
        return Response({"redirect_to": redirect_url}, status=HTTP_200_OK)


class ResetPasswordView(GenericAPIView):
    permission_classes = [IsAuthenticated, IsCoordinator | IsTrainer]
    serializer_class = ResetPasswordSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        response = Response({"message": "Password Reset Successfully"})
        user.set_password(serializer.validated_data.get("password"))
        user.is_reset_password_needed = False
        user.save()

        return response
    
class RegisterView(CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return None
        
class ActivateAccountView(View):
    def get(self, request, uidb64, token, parent_id, *args, **kwargs):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
            parent_id = force_str(urlsafe_base64_decode(parent_id))
            parent = Parent.objects.get(pk=parent_id)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None
            parent = None

        if user is not None and parent is not None and default_token_generator.check_token(user, token):
            with transaction.atomic():
                user.is_active = True
                user.save()
                parent.user = user
                parent.save()
            return HttpResponse('Thank you for your email confirmation. Now you can log in to your account.')
        else:
            return HttpResponse('Activation link is invalid!')