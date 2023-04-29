from django.contrib import admin

from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Администрирование модели пользователей."""

    list_display = ("id", "username", "email", "role")
    """Поля, которые будут отображаться в списке объектов."""

    search_fields = ("username",)
    """Поля, по которым можно будет искать объекты в админке."""
