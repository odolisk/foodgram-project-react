from rest_framework import viewsets
from users.pagination import CustomPagination

from .filters import IngredientStartFilter, RecipeFilter
from .models import Ingredient, Recipe, Tag
from .permissions import IsAuthorOrAdminOrReadOnly
from .serializers import (
    IngredientSerializer,
    RecipeCreateSerializer, RecipeShowSerializer,
    TagSerializer
    )


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (IsAuthorOrAdminOrReadOnly, )
    pagination_class = CustomPagination
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeShowSerializer
        return RecipeCreateSerializer


class TagViewSet(viewsets.ModelViewSet):
    serializer_class = TagSerializer
    queryset = Tag.objects.all()


class IngredientViewSet(viewsets.ModelViewSet):
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()
    filterset_class = IngredientStartFilter
    http_method_names = ('get', )


def ManageRecipe():
    pass


def ShoppingCart():
    pass
