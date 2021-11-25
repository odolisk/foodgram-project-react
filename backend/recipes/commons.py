from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from .models import Recipe


class ShortRecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField(required=True)

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class ShowRecipeSerializerMixin:

    def to_representation(self, instance):
        return ShortRecipeSerializer(
            instance.recipe,
            context=self.context).data
