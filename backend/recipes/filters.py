from django.db.models import Q
from django_filters import rest_framework as filters

from .models import Ingredient, Recipe, Tag


class IngredientStartFilter(filters.FilterSet):
    """Filter Ingredients by started with query param name."""
    name = filters.CharFilter(
        field_name='name',
        lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipeFilter(filters.FilterSet):
    """Filter Recipe by tags(slug), by author (id), by present in
    shopping cart (bool) and present in favorite of current user (bool)."""
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all())
    is_favorited = filters.BooleanFilter(method='get_in_favorite')
    is_in_shopping_cart = filters.BooleanFilter(method='get_in_shopping_cart')

    class Meta:
        model = Recipe
        fields = ('author',)

    def __get_in(self, queryset, name, value, field_name):
        field = Q(**{field_name: self.request.user})
        if value:
            return queryset.filter(field)
        return queryset

    def get_in_favorite(self, queryset, name, value):
        return self.__get_in(queryset, name, value, 'favor_recipe__user')

    def get_in_shopping_cart(self, queryset, name, value):
        return self.__get_in(queryset, name, value, 'shopping_recipe__user')
