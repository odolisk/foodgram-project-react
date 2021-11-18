from django.contrib import admin

from .models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                     ShoppingCart, Tag)


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    verbose_name = 'Ингредиент'
    verbose_name_plural = 'Ингредиенты'
    extra = 0


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'measurement_unit')
    search_fields = ('name',)
    inlines = (RecipeIngredientInline,)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'author')
    search_fields = ('name', 'author__username', 'tags__name')
    readonly_fields = ('pub_date', 'in_favorites')
    list_filter = ('name', 'author')
    filter_horizontal = ('tags',)
    inlines = (RecipeIngredientInline,)

    def in_favorites(self, obj):
        return obj.favor_recipe.count()

    in_favorites.short_description = 'Добавили в избранное'


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'recipe')
    search_fields = ('user__username', 'recipe__name')


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'recipe')
    search_fields = ('user__username', 'recipe__name')


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'color', 'slug')
    search_fields = ('name', 'color')
    prepopulated_fields = {'slug': ('name',)}
