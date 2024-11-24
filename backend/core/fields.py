import base64
import uuid

from django.core.files.base import ContentFile
from rest_framework import serializers


class Base64ImageField(serializers.ImageField):
    """Сериализатор для отправки изображенией в JSON формате"""

    def to_internal_value(self, data):
        try:
            if isinstance(data, str) and data.startswith('data:image'):
                format, imgstr = data.split(';base64,')
                ext = format.split('/')[-1]
                data = ContentFile(
                    base64.b64decode(imgstr), name=f'{uuid.uuid4()}.{ext}'
                )
        except Exception:
            raise serializers.ValidationError(
                'Ошибки валидации в стандартном формате DRF'
            )
        return super().to_internal_value(data)
