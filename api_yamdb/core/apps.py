from django.apps import AppConfig


class CoreConfig(AppConfig):
    """
    Конфигурация приложения Core.

    default_auto_field: str
        Название класса поля, который будет использоваться
        в качестве первичного ключа модели.
    name: str
        Название приложения.
    """
    default_auto_field = "django.db.models.BigAutoField"
    name = "core"
