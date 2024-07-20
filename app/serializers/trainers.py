from rest_framework import serializers

from app.models import (
    Trainer,
    TrainerFromSchool,
    TrainerSchedule,
)
from app.services.trainers import TrainerService


class TrainerCreateUpdateSerializer(serializers.ModelSerializer):
    id = serializers.CharField(read_only=True)

    class Meta:
        model = Trainer
        fields = [
            "id",
            "first_name",
            "last_name",
            "phone_contact",
            "email_contact",
        ]

    def create(self, validated_data):
        validated_data["user"] = TrainerService.create_user_for_trainer_and_send_emai(
            username=f'{self.validated_data["first_name"]}.{self.validated_data["last_name"]}',
            trainer_email=self.validated_data["email_contact"]
        )
        print(validated_data["user"])
        trainer = Trainer.objects.create(
            user = validated_data["user"],
            first_name=self.validated_data["first_name"],
            last_name=self.validated_data["last_name"],
            phone_contact=self.validated_data["phone_contact"],
            email_contact=self.validated_data["email_contact"],
        )
        TrainerFromSchool.objects.create(
            trainer=trainer,
            # TODO: fix this for multiple schools
            school=self.context['request'].user.user_school.all().first(),
        )
        return trainer


class TrainerFromSchoolSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source="trainer.first_name")
    last_name = serializers.CharField(source="trainer.last_name")
    phone_contact = serializers.CharField(source="trainer.phone_contact")
    email_contact = serializers.CharField(source="trainer.email_contact")

    class Meta:
        model = TrainerFromSchool
        fields = ['trainer', 'first_name', 'last_name', 'phone_contact', 'email_contact']


class TrainerScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainerSchedule
        fields = '__all__'