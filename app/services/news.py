from app.models import News

class NewsService:
    @staticmethod
    def get_news_by_school(school):
        return News.objects.filter(school=school).order_by("created_at")
