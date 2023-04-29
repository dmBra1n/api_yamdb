from django.contrib import admin

from .models import Category, Comment, Genre, Review, Title


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """
    Администраторская панель для модели Category.
    Поля: pk, name, slug.
    """

    list_display = (
        "pk",
        "name",
        "slug",
    )


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    """
    Администраторская панель для модели Genre.
    Поля: pk, name, slug.
    """

    list_display = (
        "pk",
        "name",
        "slug",
    )


@admin.register(Title)
class TitleAdmin(admin.ModelAdmin):
    """
    Администраторская панель для модели Title.
    Поля: pk, name, year, description, genres, category.
    """

    list_display = (
        "pk",
        "name",
        "year",
        "description",
        "get_genres",
        "category",
    )
    list_editable = ("category",)
    search_fields = (
        "name",
        "description",
    )

    def get_genres(self, obj):
        """
        Возвращает список жанров, связанных с объектом.
        """
        return ", ".join([str(genre) for genre in obj.genres.all()])

    get_genres.short_description = "Жанры"


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """
    Администраторская панель для модели Review.
    Поля: pk, title, author, text, pub_date, score.
    """

    list_display = ("pk", "title", "author", "text", "pub_date", "score")


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """
    Администраторская панель для модели Comment.
    Поля: pk, review, author, text, pub_date.
    """

    list_display = (
        "pk",
        "review",
        "author",
        "text",
        "pub_date",
    )
