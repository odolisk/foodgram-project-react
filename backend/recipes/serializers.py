from rest_framework import serializers
from drf_base64.fields import Base64ImageField

from .models import Ingredient, Recipe, Tag


class RecipeSerializer(serializers.ModelSerializer):

    image = Base64ImageField(required=True)

    class Meta:
        model = Recipe
        fields = ('author', 'name', 'image',
                  'text', 'ingredients', 'tags',
                  'cooking_time', 'pub_date')


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')
        ordering = ('name', )
