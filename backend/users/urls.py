from rest_framework.routers import DefaultRouter

from .views import FoodGramUserViewSet

router = DefaultRouter()
router.register('', FoodGramUserViewSet, basename='users')

urlpatterns = router.urls
