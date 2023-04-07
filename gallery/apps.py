"""
This file contains gallery app config.
"""
from django.apps import AppConfig


class ImageConfig(AppConfig):
    """
     Use the AppConfig app to specify name and fields
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'gallery'
