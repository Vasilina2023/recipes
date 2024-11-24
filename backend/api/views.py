from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import HttpResponse, Http404
from django.shortcuts import redirect
from django_filters.rest_framework import DjangoFilterBackend
from djoser import views as d_views
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import (
    AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly
)
from rest_framework.response import Response

from api.filters import RecipeFilter, IngredientFilter
from api.permissions import AdminAuthorPermission
from api.serializers import (
    AvatarSerializer, IngredientSerializer, RecipeReadSerializer,
    RecipeWriteSerializer, ShortRecipeSerializer, SubscriptionSerializer,
    TagSerializer, SubscriptionWriteSerializer
)
from core.pagination import LimitPageNumberPagination
from recipes.models import (
    Cart, Favorite, Ingredient, Recipe, Tag
)
from users.models import Subscription

User = get_user_model()


class RecipeBaseViewSet(viewsets.ModelViewSet):
    """
    Представление для модели Recipes.

    В представлении доступна фильтрация по избранному, автору, списку
    покупок и тегам. Реализованы методы по удалению и добавлению в избранное
    и в список покупок.
    """

    http_method_names = ('get', 'post', 'patch', 'delete')
    queryset = Recipe.objects.all().order_by('-pub_date')
    pagination_class = LimitPageNumberPagination
    permission_classes = (AdminAuthorPermission,)
    filter_backends = (filters.SearchFilter, DjangoFilterBackend)
    filterset_class = RecipeFilter
    filterset_fields = ('author',)

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeReadSerializer
        return RecipeWriteSerializer

    @staticmethod
    def manage_for_add_and_delete(request, model, pk):
        """Метод для добавления и удаления рецепта из коллекции."""
        user = request.user
        recipe_in_collection = get_object_or_404(Recipe, id=pk)
        recipe_current_user = model.objects.filter(user=user, recipe__id=pk)
        is_a_recipe = recipe_current_user.exists()
        if request.method == 'POST':
            if is_a_recipe:
                return Response({
                    'errors': 'Рецепт уже добавлен в список'
                }, status=status.HTTP_400_BAD_REQUEST)
            model.objects.create(user=user, recipe=recipe_in_collection)
            serializer = ShortRecipeSerializer(recipe_in_collection)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if is_a_recipe:
            recipe_current_user.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {
                'errors': 'Рецепт уже удалён'
            }, status=status.HTTP_400_BAD_REQUEST
        )

    @action(
        methods=['post', 'delete'],
        detail=True, permission_classes=[IsAuthenticated]
    )
    def shopping_cart(self, request, pk=None):
        """Метод добавляет или удаляет рецепт из корзины покупок."""
        return self.manage_for_add_and_delete(request, Cart, pk)

    @action(
        methods=['post', 'delete'],
        detail=True, permission_classes=[IsAuthenticated]
    )
    def favorite(self, request, pk=None):
        """Метод добавляет или удаляет рецепт из избранного."""
        return self.manage_for_add_and_delete(request, Favorite, pk)

    @action(detail=True, url_path='get-link')
    def get_link(self, request, pk=None):
        get_recipe = self.get_object()
        base_url = request.get_host()
        short_link = f'https://{base_url}/s/{get_recipe.short_link}'
        return Response({'short-link': short_link})

    @action(detail=False, permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        """Метод для скачивания списка покупок текущего пользователя."""
        ingredients = Ingredient.objects.filter(
            in_ir__recipe__cart__user=request.user
        ).values(
            'name', 'measurement_unit'
        ).annotate(quantity=Sum('in_ir__amount'))
        final_list = ["Список покупок\n"]
        final_list += [
            f'{ingredient["name"]} - '
            f'{ingredient["quantity"]} '
            f'({ingredient["measurement_unit"]})\n'
            for ingredient in ingredients
        ]
        response = HttpResponse(final_list, content_type='text/plain')
        response[
            'Content-Disposition'
        ] = 'attachment; filename="shopping_list.txt"'
        return response


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Представление для модели Tag."""

    http_method_names = ('get', 'post', 'patch', 'delete')
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Представление для модели Ingredients.

    Настроена фильтрация с возможностью поиск по частичному вхождению в начале
    названия ингредиента.
    """

    http_method_names = ('get', 'post', 'patch', 'delete')
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (filters.SearchFilter, DjangoFilterBackend)
    filterset_fields = ('name',)
    filterset_class = IngredientFilter
    search_fields = ('^name',)
    pagination_class = None


class UserViewSet(d_views.UserViewSet):
    """
    Представление для модели пользователя.

    Представление содержит дополнительные методы для управления аватаром и
    подписками.
    """

    http_method_names = ('get', 'post', 'put', 'delete')
    pagination_class = LimitPageNumberPagination
    permission_classes = (AllowAny,)

    def get_permissions(self):
        if self.action == 'me':
            self.permission_classes = [IsAuthenticated, ]
        return super().get_permissions()

    @action(methods=['put', 'delete'], detail=False,
            permission_classes=[IsAuthenticatedOrReadOnly],
            url_path='me/avatar', url_name='avatar')
    def avatar(self, request):
        """
        Управление аватаром.

        По умолчанию пользователь создается без аватара. Метод позволяет
        добавить или удалить аватар.
        """
        user = request.user
        if request.method == 'PUT':
            serializers = AvatarSerializer(
                user, data=request.data, partial=True
            )
            serializers.is_valid(raise_exception=True)
            serializers.save()
            return Response(
                serializers.data, status=status.HTTP_200_OK
            )
        user.avatar = None
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=['post', 'delete'],
        detail=True, permission_classes=[IsAuthenticated]
    )
    def subscribe(self, request, id=None):
        """Метод для добавления и удаления подписки на другого пользователя."""
        current_user = request.user
        subscription = get_object_or_404(User, id=id)
        subscriptions_user = Subscription.objects.filter(
            user=subscription, subscribe=current_user
        )
        user_is_subscribed = subscriptions_user.exists()
        if current_user == subscription:
            return Response(
                {
                    'errors': 'Вы не можете подписываться на самого себя'
                }, status=status.HTTP_400_BAD_REQUEST
            )

        if request.method == 'POST':
            if user_is_subscribed:
                return Response(
                    {
                        'errors': 'Вы уже подписаны на данного пользователя'
                    }, status=status.HTTP_400_BAD_REQUEST
                )
            subscriptions = Subscription.objects.create(
                user=subscription, subscribe=current_user
            )

            serializer = SubscriptionWriteSerializer(
                subscriptions, context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if user_is_subscribed:
            subscriptions_user.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {
                'errors': 'Пользователь уже удалён из избранного'
            }, status=status.HTTP_400_BAD_REQUEST
        )

    @action(
        detail=False, permission_classes=[IsAuthenticated],
        serializer_class=SubscriptionSerializer
    )
    def subscriptions(self, request):
        """
        Возвращает пользователей, на которых подписан текущий пользователь.

        В выдачу добавляются рецепты,
        количество которых можно регулировать параметром limit.
        """
        queryset = self.paginate_queryset(
            User.objects.filter(followers__subscribe=self.request.user)
        )
        print('queryset', queryset)
        serializer = self.get_serializer(
            queryset, many=True, context={'request': request}
        )
        print('serializer', serializer)
        return self.get_paginated_response(serializer.data)


def get_recipe_short_link(request, short_link):
    """Перенаправление на основную ссылку."""
    base_url = request.get_host()
    if short_link:
        recipe = get_object_or_404(Recipe, short_link=short_link)
        return redirect(f'https://{base_url}/recipes/{recipe.pk}')
    else:
        raise Http404("Короткая ссылка не существует")
