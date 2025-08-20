"""Админ-зона Блогикума."""

from django.contrib import admin

from .models import Category, Comment, Location, Post


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Админка для категорий."""

    list_display = (
        'title',
        'description',
        'slug',
        'is_published'
    )
    list_editable = ('is_published',)
    search_fields = ('title', 'description')
    prepopulated_fields = {'slug': ('title',)}
    list_filter = ('is_published',)


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    """Админка для местоположений."""

    list_display = ('name', 'is_published')
    list_editable = ('is_published',)
    search_fields = ('name',)
    list_filter = ('is_published',)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    """Админка для публикаций."""

    list_display = (
        'title',
        'pub_date',
        'author',
        'location',
        'category',
        'is_published',
        'image',
    )
    list_editable = ('is_published',)
    search_fields = (
        'title',
        'text',
        'author__username'
    )
    list_filter = (
        'is_published',
        'category',
        'location',
        'pub_date'
    )
    date_hierarchy = 'pub_date'
    raw_id_fields = ('author',)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """Админка для комментариев."""

    list_display = ('author', 'post', 'created_at', 'is_published')
    list_filter = ('is_published', 'created_at')
    search_fields = ('text',)
