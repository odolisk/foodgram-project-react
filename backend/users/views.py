from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Subscription, User
from .pagination import CustomPagination
from .serializers import (ShowSubscriptionsSerializer, SubscribeSerializer,
                          UserDetailSerializer)


class SubscriptionViewSet(viewsets.ModelViewSet):
    serializer_class = SubscribeSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        user = self.request.user
        return user.subs_subscribers.all()


class FoodGramUserViewSet(UserViewSet):
    pagination_class = CustomPagination
    http_method_names = ('get', 'post', )
    # permission_classes = (permissions.IsAuthenticated, )

    @action(detail=True, methods=('GET', 'DELETE'),
            permission_classes=(permissions.IsAuthenticated, ))
    def subscribe(self, request, id):
        author = get_object_or_404(User, id=id)
        serializer = SubscribeSerializer(
            data={'user': request.user.id, 'author': id}
        )
        if request.method == 'GET':
            serializer.is_valid(raise_exception=True)
            serializer.save(user=request.user)
            serializer = UserDetailSerializer(
                author, context={'request': request})
            return Response(
                serializer.data, status=status.HTTP_201_CREATED)

        subs = get_object_or_404(
            Subscription, user=request.user, author=author)
        subs.delete()
        return Response(f'{request.user} отписан от {subs.author}',
                        status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=('GET', ),
            permission_classes=(permissions.IsAuthenticated, ))
    def subscriptions(self, request):
        users = User.objects.filter(subs_authors__user=request.user)
        paginator = CustomPagination()
        page = paginator.paginate_queryset(users, request)
        serializer = ShowSubscriptionsSerializer(
            page, many=True, context={'request': request})

        return paginator.get_paginated_response(serializer.data)
