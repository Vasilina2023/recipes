from django.contrib.auth.models import AbstractUser
from django.db import models

from core.constants import MAX_LENGTH_TEXT, MAX_LENGTH_NAME_USER
from core.validators import username_validator


class User(AbstractUser):
    email = models.EmailField(
        verbose_name='Адрес электронной почты', max_length=MAX_LENGTH_TEXT,
        unique=True
    )
    username = models.CharField(
        verbose_name='Юзернейм', max_length=MAX_LENGTH_NAME_USER,
        validators=[username_validator], unique=True
    )
    first_name = models.CharField(
        verbose_name='Имя', max_length=MAX_LENGTH_NAME_USER
    )
    last_name = models.CharField(
        verbose_name='Фамилия', max_length=MAX_LENGTH_NAME_USER
    )
    avatar = models.ImageField(
        verbose_name='Аватар', upload_to='image/', null=True, blank=True,
        default=None
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'username', ]

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)

    def __str__(self):
        return self.username


class Subscription(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE, verbose_name='Пользователь',
        related_name='followers'
    )
    subscribe = models.ForeignKey(
        User,
        on_delete=models.CASCADE, verbose_name='Подписчик',
        related_name='following'
    )

    class Meta:
        verbose_name = 'Подписки'
        verbose_name_plural = 'Подписки'
        ordering = ('user',)
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'subscribe'], name='unique_subscribe'
            )
        ]

    def __str__(self):
        return f'{self.user}{self.subscribe}'
