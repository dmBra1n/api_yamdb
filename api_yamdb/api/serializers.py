import datetime

from django.shortcuts import get_object_or_404
from rest_framework.serializers import (
    ModelSerializer,
    SerializerMethodField,
    ValidationError,
)

from reviews.models import Category, Genre, Title


class CategorySerializer(ModelSerializer):
    class Meta:
        fields = ('name', 'slug',)
        model = Category


class GenreSerializer(ModelSerializer):
    class Meta:
        fields = ('name', 'slug',)
        model = Genre


class TitleSerializer(ModelSerializer):
    category = CategorySerializer(read_only=True)
    genres = GenreSerializer(read_only=True, many=True)
    rating = SerializerMethodField()

    class Meta:
        fields = '__all__'
        model = Title

    def get_rating(self, obj):
        rating = None
        return rating

    def get_context_data(self):
        return self.context['request'].data

    def get_category(self, slug):
        return get_object_or_404(Category, slug=slug)

    def get_genres(self, slugs):
        genres = []
        for slug in slugs:
            genre = get_object_or_404(Genre, slug=slug)
            genres.append(genre)
        return genres

    def create(self, validated_data):
        data = self.get_context_data()
        category = self.get_category(data['category'])
        genres = self.get_genres(data['genres'])
        title = Title.objects.create(category=category, **validated_data)
        title.genres.set(genres)
        return title

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.year = validated_data.get('year', instance.year)
        instance.description = validated_data.get(
            'description',
            instance.description
        )
        data = self.get_context_data()
        instance.category = self.get_category(data['category'])
        instance.genres.set(self.get_genres(data['genres']))
        instance.save()
        return instance

    def validate_year(self, year):
        if year > datetime.datetime.now().year:
            raise ValidationError(
                'Year can not be greater than the current year.'
            )
        return year
