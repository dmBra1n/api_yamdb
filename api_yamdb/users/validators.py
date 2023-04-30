import re

from django.core.exceptions import ValidationError


def validate_username(value):
    """Проверка username на корректность"""

    pattern = re.compile(r'^[\w.@+-]+')
    if value == 'me':
        raise ValidationError('Нельзя использовать "me" как имя пользователя')

    if pattern.fullmatch(value) is None:
        match = re.split(pattern, value)
        symbols = ''.join(match)
        raise ValidationError(f'В username некорректные символы: {symbols}')
