from django.contrib import admin

from .models import (Ingredient, Favourite, Recipe, RecipeIngredient,
                     ShoppingList, Subscription, Tag)


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    verbose_name = 'Ингредиент'
    verbose_name_plural = 'Ингредиенты'
    extra = 0


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'measurement_unit')
    search_fields = ('name', )
    inlines = (RecipeIngredientInline,)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'author')
    search_fields = ('name', 'author', 'tags')
    readonly_fields = ('pub_date', )
    list_filter = ('name', 'author', 'tags',)
    inlines = (RecipeIngredientInline,)


@admin.register(Favourite)
class FavouriteAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'recipe')
    search_fields = ('user', 'recipe__name')


@admin.register(ShoppingList)
class ShoppingListAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'recipe')
    search_fields = ('user', 'recipe__name')


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'author')
    search_fields = ('user', 'author')


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'color', 'slug')
    search_fields = ('name', 'color')
    prepopulated_fields = {'slug': ('name',)}
