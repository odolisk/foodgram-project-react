from rest_framework import viewsets

from .filters import IngredientStartFilter, RecipeFilter
from .models import Ingredient, Recipe, Tag
from users.pagination import CustomPagination
from .permissions import IsAuthorOrAdminOrReadOnly
from .serializers import IngredientSerializer, RecipeSerializer, TagSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    serializer_class = RecipeSerializer
    queryset = Recipe.objects.all()
    permission_classes = (IsAuthorOrAdminOrReadOnly, )
    pagination_class = CustomPagination
    filterset_class = RecipeFilter


class TagViewSet(viewsets.ModelViewSet):
    serializer_class = TagSerializer
    queryset = Tag.objects.all()


class IngredientViewSet(viewsets.ModelViewSet):
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()
    filterset_class = IngredientStartFilter


def ManageRecipe():
    pass


def ShoppingCart():
    pass
