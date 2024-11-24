from django_filters import rest_framework as filters

from recipes.models import Recipe
from users.models import User


class RecipeFilter(filters.FilterSet):
    """Фильтрация по указанным полям рецепта."""
    author = filters.ModelChoiceFilter(queryset=User.objects.all())
    tags = filters.AllValuesMultipleFilter(field_name='tags__slug')
    is_favorited = filters.BooleanFilter(
        method='filter_for_favorited'
    )
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_for_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = ('tags', 'author')

    def filter_for_shopping_cart(self, qs, name, value):
        if value and self.request.user.is_authenticated:
            return qs.filter(cart__user=self.request.user)
        return qs

    def filter_for_favorited(self, qs, name, value):
        if value and not self.request.user.is_anonymous:
            return qs.filter(in_favorites__user=self.request.user)
        return qs


class IngredientFilter(filters.FilterSet):
    """Фильтрация по частичному вхождению в наименование ингредиента."""
    name = filters.CharFilter(lookup_expr='istartswith', field_name='name')
