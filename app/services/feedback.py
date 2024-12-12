from django.shortcuts import get_object_or_404

class FeedbackService:
    @staticmethod
    def get_feedback_by_id(queryset, feedback_id):
        return get_object_or_404(queryset, pk=feedback_id)