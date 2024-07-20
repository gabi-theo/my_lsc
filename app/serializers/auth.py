from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from app.models import (
    TrainerFromSchool,
    User,
)


class SignInSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    username = serializers.CharField(write_only=True)
    token = serializers.HiddenField(default=None)
    schools = serializers.SerializerMethodField(read_only=True)
    role = serializers.SerializerMethodField(read_only=True)
    user_id = serializers.SerializerMethodField(read_only=True)
    student_ids = serializers.SerializerMethodField(read_only=True)
    trainer_id = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = [
            "username",
            "password",
            "token",
            "schools",
            "role",
            "user_id",
            "student_ids",
            "trainer_id",
        ]

    def validate(self, attrs: dict) -> dict:
        data = super().validate(attrs)
        username = attrs.get("username", None)
        password = attrs.get("password", None)

        if username is None:
            raise serializers.ValidationError(
                "A username is required to sign-in.")

        if password is None:
            raise serializers.ValidationError(
                "A password is required to sign-in.")

        user = authenticate(username=username, password=password)

        if user is None:
            raise serializers.ValidationError(
                "This combination of username and password is invalid."
            )

        if not user.is_active:
            raise serializers.ValidationError(
                "This user has been deactivated.")

        data.update(
            {"is_reset_password_needed": user.is_reset_password_needed})
        return data

    def get_schools(self, obj):
        resp_list = []
        schools = []
        # role: admin (work in progress?)
        '''
        {
            "schools": [],
            "role": null,
            "user_id": "48037275-5764-4707-9488-81cb0e5d4e48",
            "student_ids": null,
            "trainer_id": null
        }
        '''

        if obj.role == "coordinator":
            schools = obj.user_school.all()
        elif obj.role == "student":
            parent = obj.parent_user
            try:
                schools = parent.school.all()
            except Exception as e:
                schools = [parent.school]
        elif obj.role == "trainer":
            trainer = obj.trainer_user
            schools = TrainerFromSchool.objects.filter(trainer=trainer)
            schools = [school.school for school in schools]
        elif obj.role == "admin":
            schools = obj.user_school.all()

        for school in schools:
            resp_list.append({str(school.id): school.name})

        return resp_list

    def get_role(self, obj):
        return obj.role

    def get_user_id(self, obj):
        return obj.id

    def get_student_ids(self, obj):
        try:
            parent = obj.parent_user
            if parent:
                students = parent.children.all()
                return [f"{student.id}_{student.first_name}_{student.last_name}" for student in students]
        except Exception:
            return None

    def get_trainer_id(self, obj):
        try:
            trainer = obj.trainer_user
            if trainer:
                return trainer.id
        except Exception:
            return None


class ResetPasswordSerializer(serializers.Serializer):
    password = serializers.CharField()
    user = serializers.HiddenField(default=None)

    class Meta:
        fields = [
            "password",
            "user",
        ]

    def validate(self, attrs: dict) -> dict:
        attrs = super().validate(attrs)
        request = self.context["request"]

        user = request.user
        validate_password(attrs["password"])

        attrs["user"] = user

        return attrs
