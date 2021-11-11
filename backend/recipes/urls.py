from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (DownloadShoppingCartView, FavoriteView, IngredientViewSet,
                    ManageCartView, RecipeViewSet, TagViewSet)

router = DefaultRouter()
router.register('recipes', RecipeViewSet, basename='recipes')
router.register('tags', TagViewSet, basename='tags')
router.register('ingredients', IngredientViewSet, basename='ingredients')


urlpatterns = [
    path('recipes/<int:id>/favorite/', FavoriteView.as_view(),
         name='favorite_add'),
    path('recipes/<int:id>/shopping_cart/',
         ManageCartView.as_view(), name='add_to_cart'),
    path('recipes/download_shopping_cart/',
         DownloadShoppingCartView.as_view(), name='dl_shopping_cart'),
    path('', include(router.urls)),
]
