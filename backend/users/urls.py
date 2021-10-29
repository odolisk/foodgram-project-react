from rest_framework.routers import DefaultRouter

from django.urls import include, path


from .views import SubscriptionViewSet

router = DefaultRouter()
router.register('subscriptions', SubscriptionViewSet, basename='subscriptions')

urlpatterns = [
    path('users/', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
