from django.contrib import admin
from .models import Player, Injury
from .models import CustomUser
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group

class CustomUserAdmin(UserAdmin):
    model = CustomUser

    fieldsets = UserAdmin.fieldsets + (
        ('Custom Fields', {'fields': ('is_business_user',)}),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('is_business_user',)}),
    )

    list_display = ('id', 'username', 'email', 'first_name', 'last_name', 'is_active', 'date_joined')

    admin.site.unregister(Group)

admin.site.register(CustomUser, CustomUserAdmin)

admin.site.register(Player)
admin.site.register(Injury)