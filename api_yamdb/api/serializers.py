import datetime

from rest_framework.relations import SlugRelatedField
from rest_framework.serializers import (
    CharField,
    EmailField,
    ModelSerializer,
    Serializer,
    SerializerMethodField,
    ValidationError,
)
from reviews.models import Category, Comment, Genre, Review, Title
from users.models import User
from users.validators import validate_username

from django.db.models import Avg


class CategorySerializer(ModelSerializer):
    """Сериализатор модели Category"""

    class Meta:
        fields = (
            "name",
            "slug",
        )
        model = Category


class GenreSerializer(ModelSerializer):
    """Сериализатор модели Genre"""

    class Meta:
        fields = (
            "name",
            "slug",
        )
        model = Genre


class TitleSerializer(ModelSerializer):
    """Сериализатор модели Title"""

    category = CategorySerializer(read_only=True)
    genre = GenreSerializer(read_only=True, many=True)
    rating = SerializerMethodField()

    class Meta:
        fields = "__all__"
        model = Title

    def get_rating(self, obj):
        """Метод, возвращающий среднюю оценку для объекта Title."""

        if obj.reviews.exists():
            return int(obj.reviews.aggregate(Avg("score"))["score__avg"])

    def get_context_category(self):
        """Метод, получающий категорию из запроса."""

        slug = self.context["request"].data.get("category", None)
        return Category.objects.filter(slug=slug).first()

    def get_context_genres(self):
        """Метод, получающий жанры из запроса."""

        slugs = self.context["request"].data.get("genre", [])
        return Genre.objects.filter(slug__in=slugs)

    def create(self, validated_data):
        """Метод создания объекта Title."""

        category = self.get_context_category()
        genres = self.get_context_genres()
        title = Title.objects.create(category=category, **validated_data)
        title.genre.set(genres)
        return title

    def update(self, instance, validated_data):
        """Метод обновления объекта Title."""

        instance.name = validated_data.get("name", instance.name)
        instance.year = validated_data.get("year", instance.year)
        instance.description = validated_data.get(
            "description", instance.description
        )
        instance.category = self.get_context_category()
        instance.genre.set(self.get_context_genres())
        instance.save()
        return instance

    def validate_year(self, year):
        """Метод валидации года выпуска объекта Title."""

        if year > datetime.datetime.now().year:
            raise ValidationError(
                "Год не может быть больше текущего года."
            )
        return year


class ReviewSerializer(ModelSerializer):
    """Сериализатор отзывов."""

    author = SlugRelatedField(slug_field="username", read_only=True)

    class Meta:
        fields = (
            "id",
            "text",
            "author",
            "score",
            "pub_date",
        )
        model = Review

    def validate(self, data):
        """
        Проверяет, что пользователь оставил только
        один отзыв на произведение.
        """

        user = self.context["request"].user
        title_id = self.context["view"].kwargs.get("title_id")
        if user.reviews.filter(title__id=title_id).exists():
            raise ValidationError(
                "Разрешен только один отзыв на пользователя."
            )
        return data


class CommentSerializer(ModelSerializer):
    """Сериализатор коментариев."""

    author = SlugRelatedField(slug_field="username", read_only=True)

    class Meta:
        fields = (
            "id",
            "text",
            "author",
            "pub_date",
        )
        model = Comment


class UserSerializer(ModelSerializer):
    """Сериализатор рользователей."""

    class Meta:
        fields = (
            "username",
            "email",
            "first_name",
            "last_name",
            "bio",
            "role",
        )
        model = User


class MeSerializer(ModelSerializer):
    """Сериализатор пользователя для получения и изменения своего профиля."""

    class Meta:
        fields = (
            "username",
            "email",
            "first_name",
            "last_name",
            "bio",
            "role",
        )
        read_only_fields = ("role",)
        model = User


class RegistrationSerializer(Serializer):
    """Сериализатор регистрации пользователей."""

    username = CharField(
        required=True,
        max_length=150,
        validators=[validate_username],
    )
    email = EmailField(required=True, max_length=254)


class GetTokenSerializer(Serializer):
    """Сериализатор токена"""

    username = CharField(
        required=True, max_length=150, validators=[validate_username]
    )
    confirmation_code = CharField(required=True)
