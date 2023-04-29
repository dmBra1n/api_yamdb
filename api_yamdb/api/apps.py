from django.apps import AppConfig


class ApiConfig(AppConfig):
    """
    Класс для настройки приложения API.

    - default_auto_field -- определяет поле автоинкрементации для моделей,
    созданных в приложении.
    - name -- уникальное имя приложения.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "api"
