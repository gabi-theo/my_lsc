from rest_framework import serializers

from app.models import (
    DaysOff,
    Room,
    School,
)


class DaysOffSerializer(serializers.ModelSerializer):
    class Meta:
        model = DaysOff
        fields = ["first_day_off", "last_day_off", "day_off_info"]


class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ['id', 'room_name', 'capacity']


class SchoolSetupSerializer(serializers.ModelSerializer):

    user = serializers.CharField(read_only=True)

    class Meta:
        model = School
        fields = [
            "name",
            "phone_contact",
            "email_contact",
            "user",
        ]
