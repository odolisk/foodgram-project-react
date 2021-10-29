from rest_framework import viewsets

from .models import User
from .serializers import DetailSerializer, SubscriptionSerializer


class SubscriptionViewSet(viewsets.ModelViewSet):
    serializer_class = SubscriptionSerializer
    # queryset = User.objects.all()

    def get_queryset(self):
        user = self.request.user
        return user.subs_subscriber.all()

