from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers

from .models import Subscription, User


# class UserRegistrationSerializer(UserCreateSerializer):
#     class Meta(UserCreateSerializer.Meta):
#         fields = (
#             'email',
#             'username',
#             'first_name',
#             'last_name',
#             'password',
#         )


class DetailSerializer(UserSerializer):
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
        try:
            user.subs_subscriber.get(author=obj)
            return True
        except Subscription.DoesNotExist:
            return False


# class ShowFollowSerializer(serializers.ModelSerializer):
#     is_subscribed = serializers.SerializerMethodField()
#     recipes = serializers.SerializerMethodField()
#     recipes_count = serializers.SerializerMethodField()

#     class Meta:
#         model = User
#         fields = (
#             'email',
#             'id',
#             'username',
#             'first_name',
#             'last_name',
#             'is_subscribed',
#             'recipes',
#             'recipes_count')
#         read_only_fields = fields

#     def get_is_subscribed(self, obj):
#         request = self.context.get('request')
#         if not request or request.user.is_anonymous:
#             return False
#         return obj.subs_subscriber.filter(user=obj, author=request.user).exists()

#     def get_recipes(self, obj):
#         recipes = obj.recipes.all()[:settings.RECIPES_LIMIT]
#         request = self.context.get('request')
#         context = {'request': request}
#         return ShowRecipeAddedSerializer(
#             recipes,
#             many=True,
#             context=context).data

#     def get_recipes_count(self, obj):
#         return obj.recipes.count()


class SubscriptionSerializer(serializers.ModelSerializer):
    queryset = User.objects.all()
    id = serializers.ReadOnlyField()
    user = serializers.PrimaryKeyRelatedField(queryset=queryset)
    author = serializers.PrimaryKeyRelatedField(queryset=queryset)

    class Meta:
        model = Subscription
        fields = ('id', 'user', 'author')

    def validate(self, data):
        user = self.context.get('request').user
        author = data.get('author')
        request = self.context.get('request')
        is_subs = Subscription.objects.filter(
            user=user,
            author=author
        ).exists()

        if request.method == 'GET':
            if user == author or is_subs:
                raise serializers.ValidationError(
                    'Подписка существует')
        return data

    # def to_representation(self, instance):
    #     request = self.context.get('request')
    #     context = {'request': request}
    #     return ShowFollowSerializer(
    #         instance.author,
    #         context=context).data
