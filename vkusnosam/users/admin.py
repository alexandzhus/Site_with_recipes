from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.safestring import mark_safe

from users.models import User



@admin.register(User)
class UsersAdmin(admin.ModelAdmin):

    list_display = ('username', 'password', 'email', 'first_name', 'last_name', "avatar", 'age', 'interests')
    list_display_links = ('username', 'password', 'email', 'first_name', 'last_name', "avatar", 'age', 'interests')
