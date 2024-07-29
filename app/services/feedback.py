from django.shortcuts import get_object_or_404

from app.models import Feedback

class FeedbackService:
    @staticmethod
    def get_feedback_by_id(feedback_id):
        return get_object_or_404(Feedback, pk=feedback_id)

# docker exec -it my_lsc-db-1 psql -U myuser -d myapp -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"