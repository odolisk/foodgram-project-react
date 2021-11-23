from djoser.serializers import UserSerializer
from rest_framework import serializers

from recipes.commons import FavShopCartSubsRecipeSerializer
from .models import Subscription, User


class UserDetailSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        fields = ('email', 'id', 'username',
                  'first_name', 'last_name',
                  'is_subscribed')

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        return (not user.is_anonymous
                and user.subs_subscribers.filter(author=obj).exists())


class ShowSubscriptionsSerializer(UserDetailSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed', 'recipes', 'recipes_count')

    def get_recipes(self, obj):
        recipes_limit = self.context.get('recipes_limit')
        recipes = obj.recipes.all()[:recipes_limit]
        return FavShopCartSubsRecipeSerializer(recipes, many=True).data

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
        request = self.context.get('request')
        context = {'request': request}
        return ShowSubscriptionsSerializer(
            instance.author,
            context=context).data
