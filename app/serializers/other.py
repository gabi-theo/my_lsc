from rest_framework import serializers


class ImportSerializer(serializers.Serializer):
    file = serializers.FileField()