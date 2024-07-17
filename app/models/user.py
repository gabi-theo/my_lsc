from uuid import uuid4

from django.db import models
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    """
    User model manager where username is the unique identifiers
    for authentication instead of usernames.
    """

    def create_user(self, username, password, **extra_fields):
        """
        Create and save a User with the given username and password.
        """
        if not username:
            raise ValueError(_("The username must be set"))

        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save()

        return user

    def create_superuser(self, username, password, **extra_fields):
        """
        Create and save a SuperUser with the given username and password.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must have is_staff=True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser=True."))

        return self.create_user(username, password, **extra_fields)


class User(AbstractBaseUser):
    ROLE_CHOICES = (
        ("trainer", "Trainer"),
        ("student", "Student"),
        ("coordinator", "Coordinator"),
    )
    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = []

    id = models.UUIDField(primary_key=True, default=uuid4)
    username = models.CharField(max_length=50, unique=True)
    is_superuser = models.BooleanField(
        _("superuser status"),
        default=False,
        help_text=_(
            "Designates that this user has all permissions without "
            "explicitly assigning them."
        ),
    )
    is_staff = models.BooleanField(
        _("staff status"),
        default=False,
        help_text=_(
            "Designates whether the user can log into this admin site."),
    )
    is_active = models.BooleanField(
        _("active"),
        default=True,
        help_text=_(
            "Designates whether this user should be treated as active. "
            "Unselect this instead of deleting accounts."
        ),
    )
    is_reset_password_email_token_expired = models.BooleanField(default=True)
    is_reset_password_token_expired = models.BooleanField(default=True)
    role = models.CharField(max_length=20,
                            choices=ROLE_CHOICES, blank=True, null=True)
    is_reset_password_needed = models.BooleanField(default=False)
    objects = UserManager()

    def _str_(self):
        return self.get_username()

    def has_perm(self, perm, obj=None):
        return self.is_superuser

    def has_module_perms(self, app_label):
        return self.is_superuser