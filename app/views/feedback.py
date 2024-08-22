from uuid import uuid4

from rest_framework.generics import ListCreateAPIView
from rest_framework.mixins import DestroyModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_204_NO_CONTENT,
    HTTP_400_BAD_REQUEST,
)

from app.serializers import FeedbackSerializer
from app.services.feedback import FeedbackService
from app.services.school import SchoolService
from app.services.students import StudentService

class FeedbackView(ListCreateAPIView, DestroyModelMixin):
    serializer_class = FeedbackSerializer
    permission_classes = [IsAuthenticated]

    _cached_queryset = None
    _last_school_id = None
    _last_feedback_id = None

    def get(self, request, *args, **kwargs):
        print(request.user)
        feedbacks = self.get_queryset()
        serializer = self.serializer_class(feedbacks, many=True)
        return Response(data=serializer.data, status=HTTP_200_OK)
    
    def post(self, request: Request, *args, **kwargs):

        school_id = self.kwargs.get("school_id", None)

        if not school_id:
            return Response({"detail": "school id required"}, status=HTTP_400_BAD_REQUEST)
        
        student_id = request.data.get("submitted_for_student_id", None)

        submitted_by = request.user

        print(submitted_by)
        
        submitted_for_student = StudentService.get_student_by_id(student_id=student_id) if student_id else None

        school = SchoolService.get_school_by_id(school_id=school_id)
        
        data = request.data.copy()
        print(data)
        data['feedback_for_school'] = str(school.id)
        print(data)
        if submitted_by:
            data['submited_by'] = str(submitted_by.id)
            data["role_of_submiter"] = submitted_by.role
        if submitted_for_student:
            data['submited_for_student'] = str(submitted_for_student.id)

        print(f"Data passed to serializer: {data}")

        serializer = self.get_serializer(data=data)

        if not serializer.is_valid():
            return Response(data={"detail": "error serializing feedback data"} | serializer.errors, status=HTTP_400_BAD_REQUEST)
        
        serializer.save()

        return Response(data={"detail": "feedback added successfully"} | serializer.data, status=HTTP_200_OK)
    
    def destroy(self, request: Request, *args, **kwargs):

        feedback_id = self.kwargs.get("feedback_id", None)

        if not feedback_id:
            return Response({"detail": "feedback id required"}, status=HTTP_400_BAD_REQUEST)

        feedback = FeedbackService.get_feedback_by_id(self.get_queryset(), feedback_id=feedback_id)
        feedback.delete()
        
        if self._cached_queryset is not None:
            self._cached_queryset = self._cached_queryset.exclude(id=feedback_id)

        return Response({"detail": "feedback deleted successfully"}, status=HTTP_204_NO_CONTENT)
    
    def get_queryset(self):

        school_id = self.kwargs.get("school_id", None)
        feedback_id = self.kwargs.get("feedback_id", None)

        if (self._cached_queryset is not None and
            self._last_school_id == school_id and
            self._last_feedback_id == feedback_id):
            return self._cached_queryset

        queryset = self.serializer_class.Meta.model.objects.all()

        if school_id:
            queryset = queryset.filter(feedback_for_school_id=school_id)

        if feedback_id:
            queryset = queryset.filter(id=feedback_id)

        self._cached_queryset = queryset
        self._last_school_id = school_id
        self._last_feedback_id = feedback_id

        return queryset