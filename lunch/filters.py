import django_filters
from lunch import models
from django_filters import rest_framework as filters


class RestaurantFilter(django_filters.FilterSet):
    by_date = filters.DateFilter(label="by_date", method="get_by_date")

    def get_by_date(self, queryset, name, value):
        # import ipdb; ipdb.set_trace()
        return queryset

    class Meta:
        model = models.Restaurant
        fields = {"name": ["exact", "in", "icontains"]}
