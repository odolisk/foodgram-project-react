from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
from rest_framework.authtoken.models import TokenProxy

from .models import Subscription, User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('pk', 'username', 'email', 'first_name',
                    'last_name', 'is_staff', 'is_superuser')
    search_fields = ('email', 'username')
    ordering = ('pk', )


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'author')
    search_fields = ('user', 'author')


admin.site.unregister(Group)
admin.site.unregister(TokenProxy)
