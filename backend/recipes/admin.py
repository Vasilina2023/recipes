from django.contrib import admin

from recipes.models import (
    Cart, Favorite, Ingredient, IngredientRecipe, Recipe, Tag, TagRecipe
)

admin.site.empty_value_display = 'Не задано'


class IngredientRecipeInline(admin.TabularInline):
    model = IngredientRecipe
    extra = 1


class TagRecipeInline(admin.TabularInline):
    model = TagRecipe
    extra = 1


class RecipesAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'author', 'count_favorites', 'short_link'
    )
    list_filter = ('tags',)
    search_fields = ('name', 'author',)
    inlines = (IngredientRecipeInline, TagRecipeInline)

    def count_favorites(self, obj):
        return obj.in_favorites.count()


class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')


class IngredientsAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    list_filter = ('name',)


admin.site.register(Tag, TagAdmin)
admin.site.register(Ingredient, IngredientsAdmin)
admin.site.register(Recipe, RecipesAdmin)
