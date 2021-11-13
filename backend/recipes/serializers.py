import base64
import imghdr
import uuid

import six

from rest_framework import serializers

from django.core.files.base import ContentFile

from users.serializers import UserDetailSerializer
from .models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                     ShoppingCart, Tag, User)


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, six.string_types):
            if 'data:' in data and ';base64,' in data:
                header, data = data.split(';base64,')
            try:
                decoded_file = base64.b64decode(data)
            except TypeError:
                self.fail('invalid_image')
            file_name = str(uuid.uuid4())[:12]
            file_extension = self.get_file_extension(file_name, decoded_file)
            complete_file_name = "%s.%s" % (file_name, file_extension, )
            data = ContentFile(decoded_file, name=complete_file_name)

        return super(Base64ImageField, self).to_internal_value(data)

    def get_file_extension(self, file_name, decoded_file):
        extension = imghdr.what(file_name, decoded_file)
        if extension == 'jpeg':
            return 'jpg'
        return extension


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
        ordering = ('name', )


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    """
    For representation RecipeIngredient inside recipe.
    """
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')

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
    image = Base64ImageField(max_length=None, use_url=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True)
    cooking_time = serializers.IntegerField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author',
                  'ingredients', 'name',
                  'image', 'text', 'cooking_time')

    def validate_ingredients(self, ingredients):
        uniq_ingredients = {}
        for ingredient in ingredients:
            if int(ingredient.get('amount')) < 1:
                err_data = {'ingredients': ('Количество ингредиента '
                                            'должно быть не меньше 1')}
                raise serializers.ValidationError(err_data)
            if ingredient['id'] in uniq_ingredients:
                uniq_ingredients[ingredient['id']] += ingredient['amount']
            else:
                uniq_ingredients[ingredient['id']] = ingredient['amount']
        validated_data = []
        for val_ingredient in uniq_ingredients:
            validated_data.append(
                {
                    'id': val_ingredient,
                    'amount': uniq_ingredients[val_ingredient]
                }
            )
        return validated_data

    def validate_cooking_time(self, data):
        if data < 1:
            err_data = {'cooking_time': ('Время приготовления'
                                         'должно быть не меньше 1')}
            raise serializers.ValidationError(err_data)
        return data

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        author = self.context.get('request').user
        recipe = Recipe.objects.create(author=author, **validated_data)
        for ingredient in ingredients:
            ingredient_id = ingredient.get('id')
            amount = ingredient.get('amount')
            RecipeIngredient.objects.create(
                ingredient=ingredient_id,
                recipe=recipe,
                amount=amount
            )
        recipe.tags.set(tags)
        return recipe

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        instance.tags.set(tags)
        instance.recipe_for_ingredient.all().delete()
        for ingredient in ingredients:
            RecipeIngredient.objects.create(
                ingredient=ingredient.get('id'),
                recipe=instance,
                amount=ingredient.get('amount')
            )
        instance.name = validated_data.pop('name')
        instance.text = validated_data.pop('text')
        if validated_data.get('image') is not None:
            instance.image = validated_data.pop('image')
        instance.cooking_time = validated_data.pop('cooking_time')
        instance.save()
        return instance

    def to_representation(self, instance):
        return RecipeShowSerializer(
            instance,
            context={'request': self.context.get('request')}
        ).data


class RecipeShowSerializer(serializers.ModelSerializer):
    tags = serializers.SerializerMethodField()
    author = UserDetailSerializer(read_only=True)
    image = Base64ImageField(max_length=None, use_url=True)
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

    def get_tags(self, obj):
        queryset = obj.tags.all()
        return TagSerializer(queryset, many=True).data

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        user = request.user
        return Favorite.objects.filter(recipe=obj, user=user).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        user = request.user
        return ShoppingCart.objects.filter(recipe=obj, user=user).exists()


class FavoriteSerializer(serializers.ModelSerializer):
    recipe = serializers.PrimaryKeyRelatedField(queryset=Recipe.objects.all())
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = Favorite
        fields = ('user', 'recipe')

    def validate(self, data):
        request = self.context.get('request')
        exist_err_msg = self.context.get('exist_err_msg')
        recipe = data.get('recipe')
        is_exist = Favorite.objects.filter(
            user=request.user,
            recipe=recipe).exists()

        if request.method == 'GET' and is_exist:
            data = {'errors': exist_err_msg}
            raise serializers.ValidationError(detail=data)
        return data

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return FavoriteShoppingCartRecipeSerializer(
            instance.recipe,
            context=context).data


class FavoriteShoppingCartRecipeSerializer(serializers.ModelSerializer):
    """
    For representation Recipe in Favorite and Shopping Cart.
    """
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class ShoppingCartSerializer(serializers.ModelSerializer):

    class Meta:
        model = ShoppingCart
        fields = ('id', 'user', 'recipe')
