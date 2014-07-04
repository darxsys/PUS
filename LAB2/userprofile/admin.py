from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from models import CustomUser

# Inline admin descriptor for CustomUser model
class CustomUserInline(admin.StackedInline):
    model = CustomUser
    verbose_name_plural = 'Users'

# Defining new UserAdmin
class UserAdmin(UserAdmin):
    inlines = (CustomUserInline, )

admin.site.unregister(User)
admin.site.register(User, UserAdmin)
