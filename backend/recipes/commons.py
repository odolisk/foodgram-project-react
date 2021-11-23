from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from .models import Recipe


class FavShopCartSubsRecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField(required=True)

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class CreateDeleteSerializerMixin:
    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return FavShopCartSubsRecipeSerializer(
            instance.recipe,
            context=context).data
