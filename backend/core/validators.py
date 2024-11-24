import re

from django.core.exceptions import ValidationError


def username_validator(value):
    """Кастомный валидатор имени пользователя."""
    regex = r'^[\w.@+-]+\Z'
    invalid_values = re.sub(regex, ', ', value)
    if value in invalid_values:
        raise ValidationError(
            f'Недопустимые символы: {invalid_values}'
        )
    return value


def slug_validator(value):
    """Кастомный валидатор slug"""
    regex = r'^[-a-zA-Z0-9_]+$'
    invalid_values = re.sub(regex, ', ', value)
    if value in invalid_values:
        raise ValidationError(
            f'Недопустимые символы: {invalid_values}'
        )
    return value
