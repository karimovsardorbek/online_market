from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Item, Order, Profile

class UserAdmin(BaseUserAdmin):
    fieldsets = BaseUserAdmin.fieldsets + (
        (None, {'fields': ('full_name', 'is_seller', 'is_verified')}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        (None, {'fields': ('full_name', 'is_seller', 'is_verified')}),
    )


admin.site.register(User, UserAdmin)
admin.site.register(Item)
admin.site.register(Order)
admin.site.register(Profile)