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


class CreateDeleteObjMixin:

    def create_obj(self, request, create_data):
        data = {
            'user': request.user.id,
            create_data['field_name']: create_data['id']
        }
        context = {
            'request': request,
            'exist_err_msg': create_data['err_msg']
        }
        serializer = create_data['serializer'](data=data, context=context)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete_obj(self, request, delete_data):
        subj = get_object_or_404(
            delete_data['subj_model'], id=delete_data['id'])
        obj_model = delete_data['obj_model']
        del_error_msg = delete_data['err_msg']
        del_success_msg = delete_data['success_msg']
        try:
            kwargs = {
                'user': request.user,
                delete_data['field_name']: subj}
            obj_model.objects.get(**kwargs).delete()
        except ObjectDoesNotExist:
            data = {'errors': del_error_msg}
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
        del_data = {'info': del_success_msg}
        return Response(data=del_data, status=status.HTTP_204_NO_CONTENT)


class RecipeViewSet(CreateDeleteObjMixin, viewsets.ModelViewSet):
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
