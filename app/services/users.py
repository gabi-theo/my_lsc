from typing import Optional

from app.models import User


class UserService:
    @staticmethod
    def get_user_by_username(username: str) -> Optional[User]:
        return User.objects.filter(username=username).first()

    @staticmethod
    def get_user_by_pk(pk):
        return User.objects.filter(pk=pk).first()