from django.core.exceptions import ValidationError
from django.utils import timezone


def validate_year(data):
    """
    Проверяем, что год выпуска произведения
    не может быть больше текущего.
    """

    if data > timezone.now().year:
        raise ValidationError(
            "Год выпуска произведения не может быть больше текущего."
        )
