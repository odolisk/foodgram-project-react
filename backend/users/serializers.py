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
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        user = request.user
        if user.subs_subscribers.filter(author=obj).exists():
            return True
        return False


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
        recipes_limit = request.GET.get('recipes_limit')
        if not recipes_limit or int(recipes_limit) < 1:
            recipes = obj.recipes.all()
        else:
            recipes = obj.recipes.all()[:int(recipes_limit)]
        return FavShopCartSubsRecipeSerializer(recipes, many=True).data

    def get_recipes_count(self, obj):
        queryset = obj.recipes.all()
        return queryset.count()

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        return obj.subs_authors.exists()


class SubscribeSerializer(serializers.ModelSerializer):
    queryset = User.objects.all()
    user = serializers.PrimaryKeyRelatedField(queryset=queryset)
    author = serializers.PrimaryKeyRelatedField(queryset=queryset)

    class Meta:
        model = Subscription
        fields = ('id', 'user', 'author')
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=User.objects.all(),
                fields=('user', 'author'),
                message='Подписка уже существует'
            )
        ]

    def validate_author(self, value, data):
        user = data.get('user')
        author = value
        if user == author:
            raise serializers.ValidationError(
                'Нельзя подписаться на самого себя')
        return data

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return ShowSubscriptionsSerializer(
            instance.author,
            context=context).data
