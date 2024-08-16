from django.conf import settings
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import SlidingToken
from rest_framework.permissions import AllowAny

from app.utils import (
    set_token_to_header,
    set_value_to_cookie
)
from .models import User


class CookieJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):

        if request.resolver_match and hasattr(request.resolver_match.func, 'view_class'):
            view_class = request.resolver_match.func.view_class
            if hasattr(view_class, 'permission_classes'):
                permissions = view_class.permission_classes
                if AllowAny in permissions or any(issubclass(perm, AllowAny) for perm in permissions):
                    return None
                
        if (cookies := request.COOKIES) is None:
            return None

        raw_token = cookies.get(settings.AUTH_COOKIE_KEY)

        if not raw_token:
            return None

        try:
            validated_token = self.get_validated_token(raw_token)
        except (TokenError, InvalidToken):
            return None

        return self.get_user(validated_token), validated_token

    @staticmethod
    def login(user: User, response: Response) -> None:
        token = SlidingToken.for_user(user)
        cookie_expire_time = settings.SESSION_COOKIE_AGE

        set_value_to_cookie(
            response, settings.AUTH_COOKIE_KEY, token, cookie_expire_time
        )
        set_token_to_header(response, token)
