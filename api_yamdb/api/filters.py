from django_filters.rest_framework import CharFilter, FilterSet

from reviews.models import Title


class TitleFilter(FilterSet):
    """Фильтры для модели Title."""
    category = CharFilter(field_name='category__slug')
    genre = CharFilter(field_name='genre__slug')

    class Meta:
        fields = ('category', 'genre', 'name', 'year',)
        model = Title
