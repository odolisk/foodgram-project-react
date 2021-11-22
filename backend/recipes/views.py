from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from django.db.models import Sum
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404

from users.pagination import CustomPagination
from .filters import IngredientStartFilter, RecipeFilter
from .models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                     ShoppingCart, Tag)
from .permissions import IsAuthorOrAdminOrReadOnly
from .serializers import (FavoriteSerializer,
                          IngredientSerializer, RecipeCreateSerializer,
                          RecipeShowSerializer,
                          ShoppingCartSerializer,
                          TagSerializer)
from .utils import generate_PDF


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    pagination_class = CustomPagination
    filterset_class = RecipeFilter
    permission_classes = (IsAuthorOrAdminOrReadOnly,)
    http_method_names = ('get', 'post', 'put', 'patch', 'delete')

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeShowSerializer
        return RecipeCreateSerializer

    @action(methods=('get',), detail=False,
            permission_classes=[permissions.IsAuthenticated])
    def download_shopping_cart(self, request):
        # ingredients = RecipeIngredient.objects.values(
        #     'ingredient__name',
        #     'ingredient__measurement_unit'
        # ).annotate(
        #     ingredient_sum=Sum('amount')
        # ).filter(
        #     recipe__id__in=request.user.shopping_user.values('recipe_id'))
        ingredients = RecipeIngredient.objects.filter(
            recipe__id__in=request.user.shopping_user.values('recipe_id')
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(
            ingredient_sum=Sum('amount'))
        return generate_PDF(ingredients)

    def __add_to(self, request, common, pk):
        (model, serializer, del_error_msg,
         del_success_msg, exist_err_msg) = common
        if request.method == 'GET':
            user = request.user.id
            data = {'user': user, 'recipe': pk}
            context = {'request': request,
                       'exist_err_msg': exist_err_msg}
            serializer = serializer(data=data, context=context)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)
        try:
            model.objects.get(
                user=user,
                recipe=recipe).delete()
        except ObjectDoesNotExist:
            data = {'errors': del_error_msg}
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
        del_data = {'info': del_success_msg}
        return Response(data=del_data, status=status.HTTP_204_NO_CONTENT)

    @action(methods=('get', 'delete'), detail=True,
            permission_classes=[permissions.IsAuthenticated])
    def shopping_cart(self, request, pk):
        model = ShoppingCart
        serializer = ShoppingCartSerializer
        del_error_msg = 'В списке покупок нет такого рецепта.'
        del_success_msg = 'Рецепт успешно удалён из списка покупок.'
        exist_err_msg = 'Рецепт уже находится в списке покупок.'
        common = (model,
                  serializer,
                  del_error_msg,
                  del_success_msg,
                  exist_err_msg)
        return self.__add_to(request, common, pk)

    @action(methods=('get', 'delete'), detail=True,
            permission_classes=[permissions.IsAuthenticated])
    def favorite(self, request, pk):
        model = Favorite
        serializer = FavoriteSerializer
        del_error_msg = 'В избранном нет такого рецепта.'
        del_success_msg = 'Рецепт успешно удалён из избранного.'
        exist_err_msg = 'Рецепт уже находится в избранном.'
        common = (model,
                  serializer,
                  del_error_msg,
                  del_success_msg,
                  exist_err_msg)
        return self.__add_to(request, common, pk)


class TagViewSet(viewsets.ModelViewSet):
    serializer_class = TagSerializer
    queryset = Tag.objects.all()
    http_method_names = ('get',)


class IngredientViewSet(viewsets.ModelViewSet):
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()
    filterset_class = IngredientStartFilter
    http_method_names = ('get',)
