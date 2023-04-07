"""
This module defines Django admin representing user .
This admin associated with its respective User model.
"""
from django.contrib import admin
from account.models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """
    Class UserAdmin display all the fields of User model in panel
    """
    list_display = ('id', 'first_name', 'last_name', 'username', 'email', 'contact',
                    'password', 'token', 'created_at', 'updated_at')
