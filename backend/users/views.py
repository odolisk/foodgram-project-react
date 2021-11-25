from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from foodgram_api.mixins import CreateDeleteObjMixin
from foodgram_api.pagination import CustomPagination
from .models import Subscription, User
from .serializers import ShowSubscriptionsSerializer, SubscribeSerializer


class FoodGramUserViewSet(CreateDeleteObjMixin, UserViewSet):
    pagination_class = CustomPagination
    http_method_names = ('get', 'post', 'delete')

    def destroy(self, request, *args, **kwargs):
        data = {'detail': 'Метод \"DELETE\" не разрешен.'}
        return Response(data=data, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @action(detail=True, methods=('get', 'delete'),
            url_path='subscribe',
            permission_classes=(permissions.IsAuthenticated,))
    def subscribe(self, request, id):
        author = get_object_or_404(User, id=id)
        if request.method == 'GET':
            data = {
                'serializer': SubscribeSerializer,
                'id': author.id,
                'err_msg': 'exist',
                'field_name': 'author'
            }
            return self.create_obj(request, data)
        data = {
            'obj_model': Subscription,
            'subj_model': User,
            'id': author.id,
            'err_msg': 'Вы не подписаны на этого автора',
            'success_msg': f'{request.user} отписан от {author}',
            'field_name': 'author'
        }
        return self.delete_obj(request, data)

    @action(detail=False, methods=('GET',),
            permission_classes=(permissions.IsAuthenticated,))
    def subscriptions(self, request):
        users = User.objects.filter(authors__user=request.user)
        page = self.paginator.paginate_queryset(users, request)
        serializer = ShowSubscriptionsSerializer(
            page,
            many=True,
            context={'request': request}
        )
        return self.paginator.get_paginated_response(serializer.data)
