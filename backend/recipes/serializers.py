from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from users.serializers import UserDetailSerializer

from .commons import FavShopCartSubsRecipeSerializer
from .models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                     ShoppingCart, Tag, User)


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
    name = serializers.SlugRelatedField(
        read_only=True,
        slug_field='name'
    )
    measurement_unit = serializers.SlugRelatedField(
        read_only=True,
        slug_field='measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount', 'measurement_unit', 'name')


class RecipeCreateSerializer(serializers.ModelSerializer):
    author = UserDetailSerializer(read_only=True)
    ingredients = AddIngredientToRecipeSerializer(many=True)
    image = Base64ImageField(required=True)
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
        # Т.к. переопределён метод Create, без этой валидации
        # вполне возможно сохранять в базу cooking_time = 0
        if data < 1:
            err_data = {'cooking_time': ('Время приготовления '
                                         'должно быть не меньше 1')}
            raise serializers.ValidationError(err_data)
        return data

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        author = self.context.get('request').user
        recipe = Recipe.objects.create(author=author, **validated_data)
        obj = []
        for ingredient in ingredients:
            ingredient_id = ingredient.get('id')
            amount = ingredient.get('amount')
            obj.append(
                RecipeIngredient(
                    ingredient=ingredient_id,
                    recipe=recipe,
                    amount=amount))
        RecipeIngredient.objects.bulk_create(obj)
        recipe.tags.set(tags)
        return recipe

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags', None)
        if tags is not None:
            instance.tags.set(tags)

        existent_ingrs = instance.ingredients.all()
        ingredients_data = validated_data.pop('ingredients', None)
        for ex_ing in existent_ingrs:
            if ex_ing not in ingredients_data:
                RecipeIngredient.objects.get(
                    recipe=instance,
                    ingredient=ex_ing).delete()

        if ingredients_data is not None:
            for ingredient_data in ingredients_data:
                ingredient, exist = RecipeIngredient.objects.get_or_create(
                    recipe=instance,
                    ingredient=ingredient_data['id'])
                ingredient.amount = ingredient_data['amount']
                ingredient.save()
        super().update(instance, validated_data)
        return instance

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

    def get_is_any(self, obj, model):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        user = request.user
        return model.objects.filter(recipe=obj, user=user).exists()

    def get_is_favorited(self, obj):
        return self.get_is_any(obj, Favorite)

    def get_is_in_shopping_cart(self, obj):
        return self.get_is_any(obj, ShoppingCart)


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
        return FavShopCartSubsRecipeSerializer(
            instance.recipe,
            context=context).data


class ShoppingCartSerializer(serializers.ModelSerializer):
    recipe = serializers.PrimaryKeyRelatedField(queryset=Recipe.objects.all())
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = ShoppingCart
        fields = ('user', 'recipe')

    def validate(self, data):
        request = self.context.get('request')
        exist_err_msg = self.context.get('exist_err_msg')
        recipe = data.get('recipe')
        is_exist = ShoppingCart.objects.filter(
            user=request.user,
            recipe=recipe).exists()

        if request.method == 'GET' and is_exist:
            data = {'errors': exist_err_msg}
            raise serializers.ValidationError(detail=data)
        return data

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return FavShopCartSubsRecipeSerializer(
            instance.recipe,
            context=context).data
