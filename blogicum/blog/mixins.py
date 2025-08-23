"""Mixin'ы приложения Blog."""
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Count
from django.urls import reverse
from django.utils import timezone

from blog.models import Comment, Post


class PublishedPostsMixin:
    """Миксин для работы с постами."""

    def apply_common_annotations(self, queryset):
        """
        Применяет общие аннотации, select_related, сортировку к queryset.

        Args:
            queryset: Исходный QuerySet для обработки

        Returns:
            QuerySet: Обработанный QuerySet с аннотациями и сортировкой
        """
        return queryset.select_related(
            'author',
            'category',
            'location',
        ).annotate(
            comment_count=Count('comments'),
        ).order_by('-pub_date')

    def filter_published_posts(self, queryset):
        """
        Фильтрует только опубликованные посты.

        Args:
            queryset: Исходный QuerySet для фильтрации

        Returns:
            QuerySet: Отфильтрованный QuerySet только с опубликованными постами
        """
        return queryset.filter(
            is_published=True,
            pub_date__lte=timezone.now(),
            category__is_published=True,
        )

    def get_base_queryset(self):
        """
        Базовый QuerySet для всех постов с аннотациями.

        Returns:
            QuerySet: QuerySet всех постов с примененными аннотациями
        """
        queryset = Post.objects.all()
        queryset = self.apply_common_annotations(queryset)
        return queryset


class CommentMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Миксин для работы с комментариями."""

    model = Comment
    pk_url_kwarg = 'comment_id'
    template_name = 'blog/comment.html'

    def test_func(self):
        """
        Проверяет, является ли пользователь автором комментария.

        Returns:
            bool: True если пользователь автор, иначе False
        """
        return self.get_object().author == self.request.user

    def get_success_url(self):
        """
        Возвращает URL для перенаправления после успешного удаления.

        Returns:
            str: URL для перенаправления
        """
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': self.kwargs['post_id']},
        )
