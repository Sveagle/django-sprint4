"""Конфигурация приложения блог."""
from django.apps import AppConfig


class BlogConfig(AppConfig):
    """Конфигурация класса Blog."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'blog'
    verbose_name = 'Блог'
