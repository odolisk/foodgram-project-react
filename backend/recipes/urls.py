from rest_framework.routers import DefaultRouter

from django.urls import include, path

from .views import (IngredientViewSet, RecipeViewSet, TagViewSet,
                    ManageRecipe, ShoppingCart)


router = DefaultRouter()
router.register('recipes', RecipeViewSet, basename='recipes')
router.register('tags', TagViewSet, basename='tags')
router.register('ingredients', IngredientViewSet, basename='ingredients')


urlpatterns = [
#     path('recipes/<int:recipe_id>/shopping_cart/',
#          ManageRecipe.as_view, name='manage_cart'),
#     path('recipes/download_shopping_cart/',
#          ShoppingCart.as_view, name='dl_shopping_cart'),
    path('', include(router.urls)),
]
