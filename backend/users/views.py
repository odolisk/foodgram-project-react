from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from .models import Subscription, User
from .pagination import CustomPagination
from .serializers import (ShowSubscriptionsSerializer, SubscribeSerializer,
                          UserDetailSerializer)


class FoodGramUserViewSet(UserViewSet):
    pagination_class = CustomPagination
    http_method_names = ('get')  # , 'post')  #, 'delete')

    # def destroy(self, request, *args, **kwargs):
    #     data = {'detail': 'Метод \"DELETE\" не разрешен.'}
    #     return Response(data=data, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @action(detail=True, methods=('get', 'post'),
            url_path='subscribe',
            permission_classes=(permissions.IsAuthenticated,))
    def subscribe(self, request, id):
        author = get_object_or_404(User, id=id)

        if request.method == 'DELETE':
            subs = get_object_or_404(
                Subscription, user=request.user, author=author)
            subs.delete()
            data = {'detail': f'{request.user} отписан от {author}'}
            return Response(data=data, status=status.HTTP_204_NO_CONTENT)
        serializer = SubscribeSerializer(
            data={'user': request.user.id,
                  'author': author.id}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        serializer = UserDetailSerializer(
            author, context={'request': request})
        return Response(
            serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=('GET',),
            permission_classes=(permissions.IsAuthenticated,))
    def subscriptions(self, request):
        users = User.objects.filter(subs_authors__user=request.user)
        paginator = PageNumberPagination()
        paginator.page_size = 6
        page = paginator.paginate_queryset(users, request)
        serializer = ShowSubscriptionsSerializer(
            page,
            many=True,
            context={
                'request': request,
                'recipe_limit': request.query_params.get('recipe_limit')})
        return paginator.get_paginated_response(serializer.data)
