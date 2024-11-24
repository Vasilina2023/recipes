from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.text import slugify

from core import validators
from core.constants import (
    MAX_LENGTH_NAME, MAX_LENGTH_TEXT, MAX_LENGTH_UNIT, MIN_TIME, MIN_COUNT,
    MAX_LENGTH_NAME_TAG, MAX_LENGTH_SHORT_LINK
)

User = get_user_model()


class Tag(models.Model):
    """Модель для тегов."""

    name = models.CharField(
        verbose_name='Наименование', max_length=MAX_LENGTH_NAME
    )
    slug = models.SlugField(
        unique=True, verbose_name='Слаг', db_index=True,
        max_length=MAX_LENGTH_NAME, validators=[validators.slug_validator],
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Модель для ингредиентов."""

    name = models.CharField(
        verbose_name='Наименование', unique=True, db_index=True,
        max_length=MAX_LENGTH_NAME_TAG
    )
    measurement_unit = models.CharField(
        verbose_name='Ед.изм.', max_length=MAX_LENGTH_UNIT
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'], name='unique_ingredient'
            )
        ]

    def __str__(self):
        return self.name[:MAX_LENGTH_NAME]


class Recipe(models.Model):
    """Модель для рецептов."""
    name = models.CharField(
        verbose_name='Название', max_length=MAX_LENGTH_TEXT
    )
    text = models.TextField(verbose_name='Текстовое описание рецепта')
    ingredients = models.ManyToManyField(
        Ingredient, through='IngredientRecipe',
        verbose_name='Ингриедиенты', db_index=True
    )
    tags = models.ManyToManyField(
        Tag, through='TagRecipe', verbose_name='Тег', db_index=True
    )
    cooking_time = models.PositiveSmallIntegerField(
        validators=(
            MinValueValidator(
                MIN_TIME, message='Минимальное время приготовления 1'
            ),
        ),
        verbose_name='Время приготовления в минутах'
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации', auto_now_add=True
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name='Автор', db_index=True
    )
    image = models.ImageField(
        verbose_name='Картинка', upload_to='image/', null=True, blank=True
    )
    short_link = models.SlugField(unique=True, blank=True)

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        default_related_name = 'recipe'

    def save(self, *args, **kwargs):
        if not self.short_link:
            self.short_link = slugify(
                self.name, allow_unicode=True
            )[:MAX_LENGTH_SHORT_LINK]
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class TagRecipe(models.Model):
    """Промежуточная модель для тегов и рецептов."""
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)

    class Meta:
        ordering = ('-id',)
        verbose_name = 'Промежуточная таблица для тегов рецептов'
        verbose_name_plural = 'Промежуточные таблицы для тегов рецептов'
        constraints = [
            models.UniqueConstraint(
                fields=['tag', 'recipe'], name='unique_tag_recipe'
            )
        ]

    def __str__(self):
        return f'Тег {self.tag} у рецепта {self.recipe}'[:MAX_LENGTH_TEXT]


class IngredientRecipe(models.Model):
    """Промежуточная модель для ингредиентов, их количества и рецептов."""
    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE, related_name='in_ir'
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE,
        related_name='recipe_ingredient'
    )
    amount = models.PositiveSmallIntegerField(
        validators=(
            MinValueValidator(
                MIN_COUNT, message='Минимальное количество ингридиентов 1'
            ),
        ),
        verbose_name='Количество'
    )

    class Meta:
        ordering = ('-id',)
        verbose_name = 'Промежуточная таблица для ингредиентов рецептов'
        verbose_name_plural = 'Промежуточные таблицы для ингредиентов рецептов'
        constraints = [
            models.UniqueConstraint(
                fields=['ingredient', 'recipe'],
                name='unique_ingredient_recipe'
            )
        ]

    def __str__(self):
        return (
            f'Ингредиент {self.ingredient} из рецепта {self.recipe}'
        )[:MAX_LENGTH_TEXT]


class Cart(models.Model):
    """Модель для рецептов в списке покупок пользователя."""
    recipe = models.ForeignKey(
        verbose_name="Рецепты в корзине", to=Recipe, on_delete=models.CASCADE,
        related_name='cart'
    )
    user = models.ForeignKey(
        verbose_name="Пользователь", to=User, on_delete=models.CASCADE,
    )

    class Meta:
        ordering = ('-id',)
        verbose_name = 'Рецепт в корзине'
        verbose_name_plural = 'Рецепты в корзине'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'user'], name='unique_cart_recipe'
            )
        ]


class Favorite(models.Model):
    """Модель для рецептов в списке избранных рецептов пользователя."""
    recipe = models.ForeignKey(
        verbose_name="Понравившиеся рецепты", related_name="in_favorites",
        to=Recipe, on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        verbose_name="Пользователь", related_name="favorites",
        to=User, on_delete=models.CASCADE,
    )

    class Meta:
        ordering = ('-id',)
        verbose_name = 'Рецепт в избранном'
        verbose_name_plural = 'Рецепты в избранном'
        default_related_name = 'favorite'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'user'], name='unique_favorite_recipe'
            )
        ]
