import os

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from reportlab.lib.colors import black, blue
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

from rest_framework import permissions, status, viewsets
from rest_framework.parsers import JSONParser, MultiPartParser
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
    parser_classes = (MultiPartParser, JSONParser)
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
    http_method_names = ('get', )


class IngredientViewSet(viewsets.ModelViewSet):
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()
    filterset_class = IngredientStartFilter
    http_method_names = ('get', )


class ManageCartView(FavoriteView):
    common_model = ShoppingCart
    common_serializer = ShoppingCartSerializer
    common_del_error_msg = 'В списке покупок нет такого рецепта.'
    common_exist_err_msg = 'Рецепт уже находится в списке покупок.'


class DownloadShoppingCartView(APIView):
    permission_classes = (permissions.IsAuthenticated, )

    def get(self, request):
        pivot_list = {}
        ingredients = RecipeIngredient.objects.filter(
            recipe__shopping_recipe__user=request.user).values_list(
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
        folder = settings.FONTS_PATH
        ttfFile = os.path.join(folder, 'PTAstraSans-Regular.ttf')
        pdfmetrics.registerFont(TTFont('PTAstraSans', ttfFile, 'UTF-8'))

        doc = canvas.Canvas(response, pagesize=A4)

        logo_path = os.path.join(settings.STATIC_ROOT, 'logo.png')
        logo = ImageReader(logo_path)
        doc.drawImage(logo, 30, 710, mask='auto')

        doc.setFillColor(blue)
        doc.drawString(270, 820, ('http://odolisk.ru'))

        doc.setFillColor(black)
        doc.setFont('PTAstraSans', 32)
        doc.drawString(250, 770, 'Foodgram')

        doc.setFont('PTAstraSans', 18)
        doc.drawString(170, 720,  'сайт вкусных рецептов для програмистов')

        doc.setDash([1, 1, 3, 3, 1, 4, 4, 1], 0)
        doc.setLineWidth(1)
        doc.line(30, 690, 575, 690)

        doc.setDash(1, 0)
        doc.setFillColor(black)
        doc.setFont('PTAstraSans', 24)
        doc.drawString(120, 630, 'Список необходимых ингредиентов')

        doc.setLineWidth(2)
        doc.line(120, 620, 490, 620)

        doc.setFont('PTAstraSans', 16)
        height = 570
        marker_sym = chr(8226)
        for (name, params) in pivot_list.items():
            amount = params['amount']
            mes_unit = params['measurement_unit']
            list_elem = f'{marker_sym} {name} - {amount} {mes_unit}'
            doc.drawString(75, height, list_elem)
            height -= 20
        doc.showPage()
        doc.save()
        return response
