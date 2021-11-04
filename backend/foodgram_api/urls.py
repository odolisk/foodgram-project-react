from django.contrib import admin
from django.urls import include, path


PREFIX = 'api/'

urlpatterns = [
    path('admin/', admin.site.urls),
    path(f'{PREFIX}users/', include('users.urls')),
    path(f'{PREFIX}auth/', include('djoser.urls.authtoken')),
    path(f'{PREFIX}', include('recipes.urls')),
]
