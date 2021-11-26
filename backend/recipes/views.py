from rest_framework import permissions, viewsets
from rest_framework.decorators import action

from django.db.models import Exists, F, Sum, Q
from django.shortcuts import get_object_or_404

from foodgram_api.mixins import CreateDeleteObjMixin
from foodgram_api.pagination import CustomPagination
from .filters import IngredientStartFilter, RecipeFilter
from .models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                     ShoppingCart, Tag)
from .permissions import IsAuthorOrReadOnly
from .serializers import (FavoriteSerializer,
                          IngredientSerializer, RecipeCreateSerializer,
                          RecipeShowSerializer,
                          ShoppingCartSerializer,
                          TagSerializer)
from .utils import generate_PDF


class RecipeViewSet(CreateDeleteObjMixin, viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    pagination_class = CustomPagination
    filterset_class = RecipeFilter
    permission_classes = (IsAuthorOrReadOnly,)
    http_method_names = ('get', 'post', 'put', 'patch', 'delete')

    # def get_queryset(self):
    #     user = self.request.user
    #     # return Recipe.objects.filter(
    #     #     favor_recipe__user=user)
    #     return Recipe.objects.annotate(
    #         is_favorited=Exists(
    #             Favorite.objects.filter(
    #                 user=user,
    #                 recipe=F('recipe'))))

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeShowSerializer
        return RecipeCreateSerializer

    @action(methods=('get',), detail=False,
            permission_classes=[permissions.IsAuthenticated])
    def download_shopping_cart(self, request):
        ingredients = RecipeIngredient.objects.filter(
            recipe__id__in=request.user.shopping_user.values('recipe_id')
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(
            ingredient_sum=Sum('amount'))
        return generate_PDF(ingredients)

    @action(methods=('get', 'delete'), detail=True,
            permission_classes=[permissions.IsAuthenticated])
    def shopping_cart(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        if request.method == 'GET':
            data = {
                'serializer': ShoppingCartSerializer,
                'id': recipe.id,
                'err_msg': 'Рецепт уже находится в списке покупок.',
                'field_name': 'recipe'
            }
            return self.create_obj(request, data)
        data = {
            'obj_model': ShoppingCart,
            'subj_model': Recipe,
            'id': recipe.id,
            'err_msg': 'В списке покупок нет такого рецепта.',
            'success_msg': 'Рецепт успешно удалён из списка покупок.',
            'field_name': 'recipe'
        }
        return self.delete_obj(request, data)

    @action(methods=('get', 'delete'), detail=True,
            permission_classes=[permissions.IsAuthenticated])
    def favorite(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        if request.method == 'GET':
            data = {
                'serializer': FavoriteSerializer,
                'id': recipe.id,
                'err_msg': 'Рецепт уже находится в избранном.',
                'field_name': 'recipe'
            }
            return self.create_obj(request, data)
        data = {
            'obj_model': Favorite,
            'subj_model': Recipe,
            'id': recipe.id,
            'err_msg': 'В избранном нет такого рецепта.',
            'success_msg': 'Рецепт успешно удалён из избранного.',
            'field_name': 'recipe'
        }
        return self.delete_obj(request, data)


class TagViewSet(viewsets.ModelViewSet):
    serializer_class = TagSerializer
    queryset = Tag.objects.all()
    pagination_class = None
    http_method_names = ('get',)


class IngredientViewSet(viewsets.ModelViewSet):
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()
    pagination_class = None
    filterset_class = IngredientStartFilter
    http_method_names = ('get',)
