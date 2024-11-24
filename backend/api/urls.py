from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import (
    IngredientViewSet, RecipeBaseViewSet, TagViewSet,
    UserViewSet
)

app_name = 'api'

router_v_1 = DefaultRouter()
router_v_1.register('users', UserViewSet, basename='users')
router_v_1.register('recipes', RecipeBaseViewSet, basename='recipes')
router_v_1.register('tags', TagViewSet, basename='tags')
router_v_1.register('ingredients', IngredientViewSet, basename='ingredients')

urlpatterns = [
    path('', include(router_v_1.urls)),
    path('auth/', include('djoser.urls.authtoken')),
    path('auth/', include('djoser.urls')),
]
