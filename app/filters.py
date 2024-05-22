import django_filters
from django.db.models import Q

from app.models import AbsentStudent


class AbsenceFilter(django_filters.FilterSet):
    make_up_date = django_filters.DateFilter(method='filter_make_up_date')

    def filter_make_up_date(self, queryset, name, value):
        print(value)
        if value:
            return queryset.filter(
                Q(has_make_up_scheduled=True) &
                (
                    Q(choosed_make_up_session_for_absence__date_time__date=value) |
                    Q(choosed_course_session_for_absence__date=value)
                )
            )
        return queryset

    class Meta:
        model = AbsentStudent
        fields = [
            'make_up_date'
        ]
