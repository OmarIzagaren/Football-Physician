from django.contrib import admin
from .models import Player, Injury
from .models import CustomUser
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group


admin.site.register(Player)
admin.site.register(Injury)

class CustomUserAdmin(UserAdmin):
    model = CustomUser

    fieldsets = UserAdmin.fieldsets + (
        ('Custom Fields', {'fields': ('is_business_user',)}),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('is_business_user',)}),
    )

    admin.site.unregister(Group)

admin.site.register(CustomUser, CustomUserAdmin)
