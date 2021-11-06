from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from reportlab.pdfgen import canvas
from rest_framework import permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from users.pagination import CustomPagination
from .filters import IngredientStartFilter, RecipeFilter
from .models import (Favorite, Ingredient, Recipe,
                     RecipeIngredient, ShoppingCart, Tag)
from .permissions import IsAuthorOrAdminOrReadOnly
from .serializers import (
    FavoriteSerializer, IngredientSerializer,
    RecipeCreateSerializer, RecipeShowSerializer,
    ShoppingCartSerializer,
    TagSerializer)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    pagination_class = CustomPagination
    filterset_class = RecipeFilter
    permission_classes = (IsAuthorOrAdminOrReadOnly, )
    http_method_names = ('get', 'post', 'put', 'delete', )

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeShowSerializer
        return RecipeCreateSerializer


class FavoriteView(APIView):
    common_model = Favorite
    common_serializer = FavoriteSerializer
    common_del_error_msg = 'В избранном нет такого рецепта.'
    common_exist_err_msg = 'Рецепт уже находится в избранном.'

    permission_classes = (permissions.IsAuthenticated, )
    http_method_names = ('get', 'delete', )

    def get(self, request, id):
        user = request.user.id
        data = {'user': user, 'recipe': id}
        context = {'request': request,
                   'exist_err_msg': self.common_exist_err_msg}
        serializer = self.common_serializer(data=data, context=context)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, id):
        user = request.user
        recipe = get_object_or_404(Recipe, id=id)
        try:
            self.common_model.objects.get(
                user=user,
                recipe=recipe).delete()
        except ObjectDoesNotExist:
            data = {'errors': self.common_del_error_msg}
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
        del_data = {'info': 'Рецепт успешно удалён.'}
        return Response(data=del_data, status=status.HTTP_204_NO_CONTENT)


class TagViewSet(viewsets.ModelViewSet):
    serializer_class = TagSerializer
    queryset = Tag.objects.all()
    permission_classes = (permissions.IsAuthenticated, )
    http_method_names = ('get', )


class IngredientViewSet(viewsets.ModelViewSet):
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()
    filterset_class = IngredientStartFilter
    permission_classes = (permissions.IsAuthenticated, )
    http_method_names = ('get', )


class ManageCartView(FavoriteView):
    model = ShoppingCart
    serializer = ShoppingCartSerializer
    common_del_error_msg = 'В списке покупок нет такого рецепта.'
    common_exist_err_msg = 'Рецепт уже находится в списке покупок.'


class DownloadShoppingCartView(APIView):
    permission_classes = (permissions.IsAuthenticated, )

    def get(self, request):
        pivot_list = {}
        ingredients = RecipeIngredient.objects.filter(
            recipe__author=request.user).values_list(
            'ingredient__name', 'ingredient__measurement_unit', 'amount')
        for obj in ingredients:
            
            name, measurement_unit, amount = obj
            if name not in pivot_list:
                pivot_list[name] = {
                    'measurement_unit': measurement_unit,
                    'amount': amount
                }
            else:
                pivot_list[name]['amount'] += amount

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = ('attachment; '
                                           'filename="shopping_list.pdf"')
        page = canvas.Canvas(response)
        page.setFont('TimesNewRoman', size=24)
        page.drawString(200, 800, 'Список ингредиентов')
        page.setFont('TimesNewRoman', size=16)
        height = 750
        for i, (name, data) in enumerate(pivot_list.items(), 1):
            page.drawString(75, height, (f'<{i}> {name} - {data["amount"]}, '
                                         f'{data["measurement_unit"]}'))
            height -= 25
        page.showPage()
        page.save()
        return response


            
#         shopping_cart = request.user.shopping_cart.all()
#         buying_list = {}

#         for item in shopping_cart:
#             ingredients = RecipeIngredient.objects.filter(recipe=item.recipe)
#             for ingredient in ingredients:
#                 amount = ingredient.amount
#                 name = ingredient.ingredient.name
#                 measurement_unit = ingredient.ingredient.measurement_unit

#                 if name not in buying_list:
#                     buying_list[name] = {
#                         'measurement_unit': measurement_unit,
#                         'amount': amount
#                     }
#                 else:
#                     buying_list[name]['amount'] = (buying_list[name]['amount']
#                                                    + amount)

#         wishlist = []
#         for item in buying_list:
#             wishlist.append(f'{item} - {buying_list[item]["amount"]} '
#                             f'{buying_list[item]["measurement_unit"]} \n')

#         response = HttpResponse(wishlist, 'Content-Type: text/plain')
#         response['Content-Disposition'] = 'attachment; filename="wishlist.txt"'
#         return response
    # @action(detail=False, methods=['get'],
    #         permission_classes=[IsAuthenticated])
    # def download_shopping_cart(self, request):
    #     final_list = {}
    #     ingredients = IngredientAmount.objects.filter(
    #         recipe__cart__user=request.user).values_list(
    #         'ingredient__name', 'ingredient__measurement_unit',
    #         'amount')
    #     for item in ingredients:
    #         name = item[0]
    #         if name not in final_list:
    #             final_list[name] = {
    #                 'measurement_unit': item[1],
    #                 'amount': item[2]
    #             }
    #         else:
    #             final_list[name]['amount'] += item[2]
    #     pdfmetrics.registerFont(
    #         TTFont('Slimamif', 'Slimamif.ttf', 'UTF-8'))
    #     response = HttpResponse(content_type='application/pdf')
    #     response['Content-Disposition'] = ('attachment; '
    #                                        'filename="shopping_list.pdf"')
    #     page = canvas.Canvas(response)
    #     page.setFont('Slimamif', size=24)
    #     page.drawString(200, 800, 'Список ингредиентов')
    #     page.setFont('Slimamif', size=16)
    #     height = 750
    #     for i, (name, data) in enumerate(final_list.items(), 1):
    #         page.drawString(75, height, (f'<{i}> {name} - {data["amount"]}, '
    #                                      f'{data["measurement_unit"]}'))
    #         height -= 25
    #     page.showPage()
    #     page.save()
    #     return response