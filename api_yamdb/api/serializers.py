import datetime

from django.db.models import Avg
from rest_framework.relations import SlugRelatedField
from rest_framework.serializers import (CharField, EmailField, ModelSerializer,
                                        Serializer, SerializerMethodField,
                                        ValidationError)

from reviews.models import Category, Comment, Genre, Review, Title
from users.models import User
from users.validators import validate_username


class CategorySerializer(ModelSerializer):
    """Сериализатор модели Category"""

    class Meta:
        fields = ('name', 'slug',)
        model = Category


class GenreSerializer(ModelSerializer):
    """Сериализатор модели Genre"""

    class Meta:
        fields = ('name', 'slug',)
        model = Genre


class TitleSerializer(ModelSerializer):
    """Сериализатор модели Title"""
    category = CategorySerializer(read_only=True)
    genre = GenreSerializer(read_only=True, many=True)
    rating = SerializerMethodField()

    class Meta:
        fields = '__all__'
        model = Title

    def get_rating(self, obj):
        if obj.reviews.exists():
            return int(obj.reviews.aggregate(Avg('score'))['score__avg'])


class TitleWriteSerializer(ModelSerializer):
    category = SlugRelatedField(
        slug_field='slug', queryset=Category.objects.all()
    )
    genre = SlugRelatedField(
        slug_field='slug', queryset=Genre.objects.all(), many=True
    )

    class Meta:
        fields = '__all__'
        model = Title

    def validate_year(self, year):
        if year > datetime.datetime.now().year:
            raise ValidationError(
                'Year can not be greater than the current year.'
            )
        return year


class ReviewSerializer(ModelSerializer):
    """Сериализатор отзывов."""
    author = SlugRelatedField(slug_field='username', read_only=True)

    class Meta:
        fields = ('id', 'text', 'author', 'score', 'pub_date',)
        model = Review

    def validate(self, data):
        if self.context['request'].method == 'POST':
            user = self.context['request'].user
            title_id = self.context['view'].kwargs.get('title_id')
            if user.reviews.filter(title__id=title_id).exists():
                raise ValidationError(
                    'For every title only one review per user is allowed.'
                )
        return data


class CommentSerializer(ModelSerializer):
    """Сериализатор коментариев."""
    author = SlugRelatedField(slug_field='username', read_only=True)

    class Meta:
        fields = ('id', 'text', 'author', 'pub_date',)
        model = Comment


class UserSerializer(ModelSerializer):
    """Сериализатор рользователей."""
    class Meta:
        fields = (
            'username', 'email', 'first_name', 'last_name', 'bio', 'role',
        )
        model = User


class MeSerializer(ModelSerializer):
    """Сериализатор пользователя для получения и изменения своего профиля."""
    class Meta:
        fields = (
            'username', 'email', 'first_name', 'last_name', 'bio', 'role',
        )
        read_only_fields = ('role',)
        model = User


class RegistrationSerializer(Serializer):
    """Сериализатор регистрации пользователей."""
    username = CharField(
        required=True,
        max_length=150,
        validators=[validate_username],
    )
    email = EmailField(
        required=True,
        max_length=254
    )

    class Meta:
        fields = ('username', 'email',)


class GetTokenSerializer(Serializer):
    """Сериализатор токена"""
    username = CharField(
        required=True,
        max_length=150,
        validators=[validate_username]
    )
    confirmation_code = CharField(required=True)
