from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from users.serializers import UserDetailSerializer

from .commons import ShowRecipeSerializerMixin
from .models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                     ShoppingCart, Tag)


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    """
    For representation ingredient as is.
    """
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')
        ordering = ('name',)


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    """
    For representation RecipeIngredient inside recipe.
    """
    id = serializers.PrimaryKeyRelatedField(source='ingredient',
                                            read_only=True)
    name = serializers.StringRelatedField(source='ingredient.name',
                                          read_only=True)
    measurement_unit = serializers.StringRelatedField(
        source='ingredient.measurement_unit',
        read_only=True)

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class AddIngredientToRecipeSerializer(serializers.ModelSerializer):
    """
    For representation Ingredient inside recipes.
    """
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField(min_value=1)

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipeCreateSerializer(serializers.ModelSerializer):
    author = UserDetailSerializer(read_only=True)
    ingredients = AddIngredientToRecipeSerializer(many=True)
    image = Base64ImageField(required=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True)
    cooking_time = serializers.IntegerField(min_value=1)

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author',
                  'ingredients', 'name',
                  'image', 'text', 'cooking_time')

    def validate_ingredients(self, ingredients):
        uniq_ingredients = {}
        for ingredient in ingredients:
            uniq_ingredients[ingredient['id']] = uniq_ingredients.get(
                ingredient['id'], 0) + ingredient['amount']
        validated_data = [
            {'id': key,
             'amount': value} for key, value in uniq_ingredients.items()]
        return validated_data

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        author = self.context.get('request').user
        recipe = Recipe.objects.create(author=author, **validated_data)
        obj = [
            RecipeIngredient(
                ingredient=ing['id'],
                recipe=recipe,
                amount=ing['amount']) for ing in ingredients]
        RecipeIngredient.objects.bulk_create(obj)
        recipe.tags.set(tags)
        return recipe

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags', None)
        if tags is not None:
            instance.tags.set(tags)

        ingredients = validated_data.pop('ingredients', None)
        instance.recipe_for_ingredient.all().delete()
        obj = [
            RecipeIngredient(
                ingredient=ing['id'],
                recipe=instance,
                amount=ing['amount']) for ing in ingredients]
        RecipeIngredient.objects.bulk_create(obj)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        return RecipeShowSerializer(
            instance,
            context={'request': self.context.get('request')}
        ).data


class RecipeShowSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    author = UserDetailSerializer(read_only=True)
    image = Base64ImageField(required=True)
    ingredients = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author',
                  'ingredients', 'is_favorited',
                  'is_in_shopping_cart', 'name',
                  'image', 'text', 'cooking_time')

    def get_ingredients(self, obj):
        queryset = obj.recipe_for_ingredient.all()
        return IngredientInRecipeSerializer(queryset, many=True).data

    def __get_is_any(self, obj, model):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return model.objects.filter(recipe=obj, user=user).exists()

    def get_is_favorited(self, obj):
        return self.__get_is_any(obj, Favorite)

    def get_is_in_shopping_cart(self, obj):
        return self.__get_is_any(obj, ShoppingCart)


class FavoriteSerializer(ShowRecipeSerializerMixin,
                         serializers.ModelSerializer):

    class Meta:
        model = Favorite
        fields = ('user', 'recipe')
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=('user', 'recipe'),
                message='Рецепт уже находится в избранном.'
            )
        ]


class ShoppingCartSerializer(ShowRecipeSerializerMixin,
                             serializers.ModelSerializer):

    class Meta:
        model = ShoppingCart
        fields = ('user', 'recipe')
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=ShoppingCart.objects.all(),
                fields=('user', 'recipe'),
                message='Рецепт уже находится в списке покупок.'
            )
        ]
