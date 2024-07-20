from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_204_NO_CONTENT,
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
)

from app.models import News
from app.permissions import (
    IsCoordinator,
    IsStudent,
    IsTrainer,
)
from app.serializers import NewsSerializer
from app.services.news import NewsService


class NewsView(ListAPIView):
    serializer_class = NewsSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.request.method == 'POST':
            self.permission_classes = [IsAuthenticated, IsCoordinator]
        elif self.request.method == 'DELETE':
            self.permission_classes = [IsAuthenticated, IsCoordinator]
        elif self.request.method == 'GET':
            self.permission_classes = [
                IsAuthenticated, IsCoordinator | IsTrainer | IsStudent]
        return super(NewsView, self).get_permissions()

    def post(self, request, *args, **kwargs):

        serializer = NewsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=HTTP_200_OK)
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)

    def get(self, request, *args, **kwargs):
        school_id = kwargs.get("school_id")
        student_id = kwargs.get("student_id")

        if not school_id:
            return Response({"error": "school_id required"}, status=HTTP_400_BAD_REQUEST)

        if student_id:
            news_queryset_by_student = NewsService.get_news_by_student_and_school(
                school_id, student_id)

        serializer = NewsSerializer(news_queryset_by_student, many=True)

        return Response(serializer.data, status=HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        news_id = kwargs.get("news_id")

        if not news_id:
            return Response({"error": "news_id required"}, status=HTTP_400_BAD_REQUEST)

        try:
            news = NewsService.get_news_by_news_id(news_id)
        except News.DoesNotExist:
            return Response({"error": "News not found"}, status=HTTP_404_NOT_FOUND)

        news.delete()
        return Response(status=HTTP_204_NO_CONTENT)

    def get_queryset(self):
        return NewsService.get_news_by_school(self.request.user.user_school.all().first())
