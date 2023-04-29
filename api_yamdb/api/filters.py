from django_filters.rest_framework import FilterSet, CharFilter

from reviews.models import Title


class TitleFilter(FilterSet):
    """Фильтры для модели Title."""
    category = CharFilter(field_name='category__slug')
    genre = CharFilter(field_name='genres__slug')

    class Meta:
        """Настройки фильтрации для модели Title."""
        fields = ('category', 'genre', 'name', 'year',)
        model = Title
