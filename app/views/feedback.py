from rest_framework.generics import ListCreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_400_BAD_REQUEST,
)

from app.models import Feedback

from app.serializers import FeedbackSerializer
from app.services.feedback import FeedbackService

class FeedbackView(ListCreateAPIView):
    serializer_class = FeedbackSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request: Request, *args, **kwargs):

        feedback_id = kwargs.get("feedback_id")

        if not feedback_id:

            feedbacks = Feedback.objects.all()

            serializer = FeedbackSerializer(feedbacks, many=True)
        
            return Response(data=serializer.data, status=HTTP_200_OK)
        
        feedback = FeedbackService.get_feedback_by_id(feedback_id=feedback_id)
        
        serializer = FeedbackSerializer(feedback)

        return Response(data=serializer.data, status=HTTP_200_OK)
    
    def post(self, request: Request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data)

        if not serializer.is_valid():
            return Response(data=serializer.errors, status=HTTP_400_BAD_REQUEST)
        
        serializer.save()

        response_data = {"status": "feedback added successfully"}
        response_data.update(serializer.data)

        return Response(data=response_data, status=HTTP_200_OK)
    
    def delete(self, request: Request, *args, **kwargs):

        feedback_id = kwargs.get("feedback_id")

        if not feedback_id:
            return Response({"error": "feedback id required"}, status=HTTP_400_BAD_REQUEST)

        feedback = FeedbackService.get_feedback_by_id(feedback_id=feedback_id)
        feedback.delete()

        return Response({"status": "feedback deleted successfully"}, status=HTTP_200_OK)
    
    def get_queryset(self):
        return Feedback.objects.all()