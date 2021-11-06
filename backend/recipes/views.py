from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404

from rest_framework import permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from users.pagination import CustomPagination
from .filters import IngredientStartFilter, RecipeFilter
from .models import Favorite, Ingredient, Recipe, Tag
from .permissions import IsAuthorOrAdminOrReadOnly
from .serializers import (
    FavoriteSerializer, IngredientSerializer,
    RecipeCreateSerializer, RecipeShowSerializer,
    TagSerializer)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    pagination_class = CustomPagination
    filterset_class = RecipeFilter
    permission_classes = (IsAuthorOrAdminOrReadOnly, )
    http_method_names = ('get', 'post', 'put', 'delete', )

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeShowSerializer
        return RecipeCreateSerializer


class FavoriteView(APIView):
    queryset = Favorite.objects.all()
    permission_classes = (permissions.IsAuthenticated, )
    http_method_names = ('get', 'delete', )

    def get(self, request, id):
        user = request.user.id
        data = {'user': user, 'recipe': id}
        serializer = FavoriteSerializer(
            data=data,
            context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, id):
        user = request.user
        recipe = get_object_or_404(Recipe, id=id)
        try:
            Favorite.objects.get(
                user=user,
                recipe=recipe).delete()
        except ObjectDoesNotExist:
            data = {'errors': 'Подписка не существует.'}
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_204_NO_CONTENT)


class TagViewSet(viewsets.ModelViewSet):
    serializer_class = TagSerializer
    queryset = Tag.objects.all()
    permission_classes = (permissions.IsAuthenticated, )
    http_method_names = ('get', )


class IngredientViewSet(viewsets.ModelViewSet):
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()
    filterset_class = IngredientStartFilter
    permission_classes = (permissions.IsAuthenticated, )
    http_method_names = ('get', )


def ManageRecipe():
    pass


def ShoppingCart():
    pass
