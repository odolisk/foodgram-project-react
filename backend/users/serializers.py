from djoser.serializers import UserSerializer
from rest_framework import serializers

from django.conf import settings

from recipes.commons import ShortRecipeSerializer
from .models import Subscription, User


class UserDetailSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username',
                  'first_name', 'last_name',
                  'is_subscribed')

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        return (user.is_authenticated
                and user.subscribers.filter(author=obj).exists())


class ShowSubscriptionsSerializer(UserDetailSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed', 'recipes', 'recipes_count')

    def get_recipes(self, obj):
        param = self.context.get('request').query_params.get(
            'recipes_limit')
        try:
            recipes_limit = int(param)
            if recipes_limit < 1:
                raise ValueError
        except (ValueError, TypeError):
            recipes_limit = settings.DEFAULT_RECIPES_LIMIT
        recipes = obj.recipes.all()[:recipes_limit]
        return ShortRecipeSerializer(recipes, many=True).data

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class SubscribeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Subscription
        fields = ('user', 'author')
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=Subscription.objects.all(),
                fields=('user', 'author'),
                message='Подписка уже существует'
            )
        ]

    def validate_author(self, value):
        user = self.initial_data.get('user')
        if user == value.id:
            raise serializers.ValidationError(
                'Нельзя подписаться на самого себя')
        return value

    def to_representation(self, instance):
        return ShowSubscriptionsSerializer(
            instance.author,
            context=self.context).data
