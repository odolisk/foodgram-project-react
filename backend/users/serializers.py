from djoser.serializers import UserSerializer
from drf_base64.fields import Base64ImageField
from rest_framework import serializers

from recipes.models import Recipe
from .models import Subscription, User


class UserDetailSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        fields = ('email', 'id', 'username',
                  'first_name', 'last_name',
                  'is_subscribed')

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        user = request.user
        if user.subs_subscribers.filter(author=obj).exists():
            return True
        return False


class RecipeSubscriptionSerializer(serializers.ModelSerializer):
    image = Base64ImageField(required=True)

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class ShowSubscriptionsSerializer(UserDetailSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed', 'recipes', 'recipes_count')

    def get_recipes(self, obj):
        request = self.context.get('request')
        recipes_limit = request.GET.get('recipes_limit', 0)
        if int(recipes_limit) > 0:
            recipes = obj.recipes.all()[:int(recipes_limit)]
        else:
            recipes = obj.recipes.all()
        return RecipeSubscriptionSerializer(recipes, many=True).data

    def get_recipes_count(self, obj):
        queryset = obj.recipes.all()
        return queryset.count()

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return obj.subs_authors.exists()


class SubscribeSerializer(serializers.ModelSerializer):
    queryset = User.objects.all()
    user = serializers.PrimaryKeyRelatedField(queryset=queryset)
    author = serializers.PrimaryKeyRelatedField(queryset=queryset)

    class Meta:
        model = Subscription
        fields = ('id', 'user', 'author')

    def validate(self, data):
        user = data.get('user')
        author = data.get('author')
        if user == author:
            raise serializers.ValidationError(
                'Нельзя подписаться на самого себя')
        is_subs = Subscription.objects.filter(
            user=user, author=author).exists()

        if is_subs:
            raise serializers.ValidationError(
                'Подписка уже существует')
        return data

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return ShowSubscriptionsSerializer(
            instance.author,
            context=context).data
