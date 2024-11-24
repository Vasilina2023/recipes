from django.db import transaction
from django.shortcuts import get_object_or_404
from djoser.serializers import UserSerializer
from rest_framework import serializers, validators

from core.fields import Base64ImageField
from recipes.models import (
    Cart, Favorite, Ingredient, IngredientRecipe, Recipe, Tag
)
from users.models import Subscription, User


class IsSubscribedMixin:
    """Миксин для проверки статуса 'подписан'."""

    def get_is_subscribed(self, obj):
        return (
            self.context.get('request').user.is_authenticated
            and Subscription.objects.filter(
                subscribe=self.context.get('request').user, user=obj.id
            ).exists()
        )


class RecipesCountMixin:
    """Миксин для подсчета количества рецептов."""

    @staticmethod
    def get_recipes_count(obj):
        return Recipe.objects.filter(author=obj.id).count()


class RecipesMixin:
    """Получение рецептов с возможностью применения параметра 'limit'."""

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        queryset = Recipe.objects.filter(author=obj.id)
        if limit:
            queryset = queryset[:int(limit)]
        return ShortRecipeSerializer(queryset, many=True).data


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для тегов."""

    class Meta:
        model = Tag
        fields = ('id', 'slug', 'name')
        read_only_fields = ('__all__',)


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для ингредиентов."""

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')
        read_only_fields = ('__all__',)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        query = self.context['request'].query_params.get('query')
        if query:
            data['name'] = data['name'].filter(name__startswith=query)
            data['name'] = data['name'].filter(
                name__icontains=query)
        return data


class IngredientRecipeWriteSerializer(serializers.ModelSerializer):
    """Сериализатор для связи рецептов и ингредиентов"""

    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all()
    )
    amount = serializers.IntegerField()

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'amount')


class IngredientRecipeReedSerializer(serializers.ModelSerializer):
    """Сериализатор для связи рецептов и ингредиентов"""

    id = serializers.ReadOnlyField(source='ingredient.id')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')
    name = serializers.ReadOnlyField(source='ingredient.name')

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class AvatarSerializer(serializers.ModelSerializer):
    """Сериализатор для аватара с возможностью отправки через JSON."""

    avatar = Base64ImageField()

    class Meta:
        model = User
        fields = ('avatar',)

    def validate(self, attrs):
        avatar = attrs.get('avatar')
        if not avatar:
            raise serializers.ValidationError(
                {'avatar': 'Аватар не выбран'}
            )
        return attrs


class BaseUserSerializer(IsSubscribedMixin, UserSerializer):
    """Сериализатор для просмотра пользователя"""

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id', 'username', 'first_name', 'last_name',
            'email', 'avatar', 'is_subscribed',
        )


class CustomUserSerializer(
    RecipesMixin, RecipesCountMixin, BaseUserSerializer
):
    """Сериализатор для просмотра полной информации о пользователе"""

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count', 'avatar')

        validators = (
            validators.UniqueTogetherValidator(
                queryset=Subscription.objects.all(),
                fields=('user', 'subscribe'),
                message='Вы уже подписаны на данного пользователя'
            ),
        )


class SubscriptionSerializer(CustomUserSerializer):
    """Сериалайзер для просмотра всех подписок."""

    id = serializers.ReadOnlyField()
    email = serializers.ReadOnlyField()
    username = serializers.ReadOnlyField()
    first_name = serializers.ReadOnlyField()
    last_name = serializers.ReadOnlyField()
    avatar = Base64ImageField(read_only=True)

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count', 'avatar')


class SubscriptionWriteSerializer(CustomUserSerializer):
    """Сериалайзер для удаления/добавления подписок."""

    id = serializers.ReadOnlyField(source='user.id')
    email = serializers.ReadOnlyField(source='user.email')
    username = serializers.ReadOnlyField(source='user.username')
    first_name = serializers.ReadOnlyField(source='user.first_name')
    last_name = serializers.ReadOnlyField(source='user.last_name')
    avatar = Base64ImageField(read_only=True, source='user.avatar')

    class Meta:
        model = Subscription
        fields = ('id', 'email', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count', 'avatar')

        validators = (
            validators.UniqueTogetherValidator(
                queryset=Subscription.objects.all(),
                fields=('user', 'subscribe'),
                message='Вы уже подписаны на данного пользователя'
            ),
        )


class ShortRecipeSerializer(serializers.ModelSerializer):
    """Короткий сериализатор для чтения информации о рецепте"""

    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = ('id', 'name', 'image', 'cooking_time')


class RecipeReadSerializer(ShortRecipeSerializer):
    """Сериализатор для чтения информации о рецепте."""

    ingredients = IngredientRecipeReedSerializer(
        many=True, source='recipe_ingredient'
    )
    tags = TagSerializer(
        read_only=True,
        many=True
    )
    author = BaseUserSerializer(read_only=True)
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time'
        )

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Recipe.objects.filter(cart__user=user, id=obj.id).exists()

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Recipe.objects.filter(
            in_favorites__user=user, id=obj.id
        ).exists()


class RecipeWriteSerializer(ShortRecipeSerializer):
    """Сериализатор для записи информации о рецепте."""

    ingredients = IngredientRecipeWriteSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all()
    )
    author = serializers.SlugRelatedField(
        slug_field='username', read_only=True
    )

    class Meta:
        model = Recipe
        fields = (
            'ingredients', 'tags', 'image', 'name', 'text', 'cooking_time',
            'author'
        )

    def validate(self, data):
        ingredients = data.get('ingredients')
        tags = data.get('tags')
        if not tags:
            raise serializers.ValidationError(
                {'tags': 'Нужен хоть один тег для рецепта'}
            )
        if not ingredients:
            raise serializers.ValidationError(
                {'ingredients': 'Нужен хоть один ингридиент для рецепта'}
            )
        tag_list = []
        for tag_current in tags:
            if tag_current in tag_list:
                raise serializers.ValidationError(
                    'Тег должен быть уникальными'
                )
            tag_list.append(tag_current)
        data['tags'] = tags
        ingredient_list = []
        for ingredient_current in ingredients:
            ingredient = get_object_or_404(
                Ingredient, id=ingredient_current['id'].id
            )
            if ingredient in ingredient_list:
                raise serializers.ValidationError(
                    'Ингридиенты должны быть уникальными'
                )
            ingredient_list.append(ingredient)
            if int(ingredient_current['amount']) < 1:
                raise serializers.ValidationError(
                    {'ingredients': 'Минимальное количество ингридиентов 1'}
                )
        data['ingredients'] = ingredients
        return data

    @staticmethod
    def create_ingredients(ingredients, recipe):
        IngredientRecipe.objects.bulk_create(
            IngredientRecipe(
                recipe=recipe,
                amount=ingredient['amount'],
                ingredient=ingredient['id']
            ) for ingredient in ingredients
        )

    @transaction.atomic
    def create(self, validated_data):
        tags_data = validated_data.pop('tags')
        ingredients_data = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(
            **validated_data, author=self.context['request'].user
        )
        recipe.tags.set(tags_data)
        self.create_ingredients(ingredients=ingredients_data, recipe=recipe)
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        tags = validated_data.pop('tags')
        instance.tags.clear()
        instance.tags.set(tags)
        ingredients = validated_data.pop('ingredients')
        instance.ingredients.clear()
        self.create_ingredients(ingredients, instance)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        serializer = RecipeReadSerializer(
            instance, context={'request': self.context.get('request')}
        )
        return serializer.data


class CartSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = Cart


class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = Favorite
