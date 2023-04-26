from django_filters.rest_framework import FilterSet, CharFilter

from reviews.models import Title


class TitleFilter(FilterSet):
    category = CharFilter(field_name='category__slug')
    genre = CharFilter(field_name='genres__slug')

    class Meta:
        fields = ('category', 'genre', 'name', 'year',)
        model = Title
