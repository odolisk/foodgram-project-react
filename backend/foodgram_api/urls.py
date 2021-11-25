from django.contrib import admin
from django.urls import include, path

PREFIX = 'api'

api_patterns = [
    path('users/', include('users.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path('', include('recipes.urls'))
]

urlpatterns = [
    path('admin/', admin.site.urls),
    path(f'{PREFIX}/', include(api_patterns))
]
