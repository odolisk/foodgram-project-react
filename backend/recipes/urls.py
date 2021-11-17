from rest_framework.routers import DefaultRouter

from django.urls import include, path

from .views import (IngredientViewSet,
                    RecipeViewSet, TagViewSet)

router = DefaultRouter()
router.register('recipes', RecipeViewSet, basename='recipes')
router.register('tags', TagViewSet, basename='tags')
router.register('ingredients', IngredientViewSet, basename='ingredients')


urlpatterns = [
    path('', include(router.urls)),
]
