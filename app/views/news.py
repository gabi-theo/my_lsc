from rest_framework.generics import ListAPIView

from app.serializers import NewsSerializer
from app.services.news import NewsService

class NewsView(ListAPIView):
    serializer_class = NewsSerializer

    def get_queryset(self):
        return NewsService.get_news_by_school(self.request.user.user_school.all().first())