from django.contrib import admin

from .models import Category, Genre, Title


class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'name',
        'slug',
    )


class GenreAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'name',
        'slug',
    )


class TitleAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'name',
        'year',
        'description',
        'get_genres',
        'category'
    )
    list_editable = ('category',)
    search_fields = ('name', 'description',)

    def get_genres(self, obj):
        return ', '.join([str(genre) for genre in obj.genres.all()])

    get_genres.short_description = 'genres'


admin.site.register(Category, CategoryAdmin)

admin.site.register(Genre, GenreAdmin)

admin.site.register(Title, TitleAdmin)
