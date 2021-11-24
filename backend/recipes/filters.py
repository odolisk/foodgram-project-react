from django_filters import rest_framework as filters

from .models import Ingredient, Recipe


class IngredientStartFilter(filters.FilterSet):
    """Filter Ingredients by started with query param name."""
    name = filters.CharFilter(
        field_name='name',
        lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ()


class RecipeFilter(filters.FilterSet):
    """Filter Recipe by tags(slug), by author (id), by present in
    shopping cart (bool) and present in favorite of current user (bool)."""
    tags = filters.MultipleChoiceFilter(field_name='tags__slug')
    is_favorited = filters.BooleanFilter(method='get_in_favorite')
    is_in_shopping_cart = filters.BooleanFilter(method='get_in_shopping_cart')

    class Meta:
        model = Recipe
        fields = ('author',)

    def __get_in(self, queryset, name, value, **kwargs):
        if value:
            return queryset.filter(**kwargs)
        return queryset

    def get_in_favorite(self, queryset, name, value):
        kwargs = {
            'favor_recipe__user': self.request.user
        }
        return self.__get_in(queryset, name, value, kwargs)

    def get_in_shopping_cart(self, queryset, name, value):
        kwargs = {
            'shopping_recipe__user': self.request.user
        }
        return self.__get_in(queryset, name, value, kwargs)
