from app.models import News

class NewsService:
    @staticmethod
    def get_news_by_school(school):
        return News.objects.filter(school=school).order_by("created_at")

    @staticmethod
    def get_news_by_student_and_school(school_id, student_id):
        news_queryset = NewsService.get_news_by_school(school_id)
        return news_queryset.filter(news_for_student_id=student_id)
        
    @staticmethod
    def get_news_by_news_id(news_id):
        return News.objects.get(id=news_id)