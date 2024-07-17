from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK

from app.permissions import IsCoordinator
from app.serializers import StudentsEmailSerializer
from app.services.students import StudentService


class SendEmailToGroupsView(GenericAPIView):
    serializer_class = StudentsEmailSerializer
    permission_classes = [IsAuthenticated, IsCoordinator]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if serializer.validated_data["send_mail"]:
            StudentService.send_emails_to_students_in_groups(
                groups=serializer.validated_data["groups"],
                subject=serializer.validated_data["subject"],
                message=serializer.validated_data["message"],
            )
        return Response({"message": "Mails sent successfully"}, HTTP_200_OK)
