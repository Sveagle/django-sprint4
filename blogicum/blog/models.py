"""
Модуль models.py определяет основные модели приложения blog.

Содержит следующие модели:
- Category - модель тематической категории для публикаций
- Location - модель географической метки для публикаций
- Post - основная модель публикаций (постов)
"""

from django.contrib.auth import get_user_model
from django.db import models
from django.utils.text import Truncator

from blog.constants import MAX_LENGTH

User = get_user_model()


class PublishedCreatedModel(models.Model):
    """Абстрактная модель с полями is_published и created_at."""

    is_published = models.BooleanField(
        default=True,
        verbose_name='Опубликовано',
        help_text='Снимите галочку, чтобы скрыть публикацию.',
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Добавлено',
    )

    class Meta:
        """Мета-класс базовой модели."""

        abstract = True

    def _truncate_str(self, text):
        return Truncator(text).chars(MAX_LENGTH)


class Category(PublishedCreatedModel):
    """Модель тематической категории для публикаций.

    Атрибуты:
        title: Название категории
        description: Подробное описание категории
        slug: Уникальный идентификатор для URL
        is_published: Флаг публикации
        created_at: Дата создания
    """

    title = models.CharField(
        max_length=256,
        verbose_name='Заголовок',
    )
    description = models.TextField(verbose_name='Описание')
    slug = models.SlugField(
        unique=True,
        verbose_name='Идентификатор',
        help_text=(
            'Идентификатор страницы для URL; '
            'разрешены символы латиницы, цифры, дефис и подчёркивание.'
        )
    )

    class Meta:
        """Мета-класс для модели Category."""

        verbose_name = 'категория'
        verbose_name_plural = 'Категории'

    def __str__(self) -> str:
        return self._truncate_str(self.title)


class Location(PublishedCreatedModel):
    """Модель географической метки для публикаций.

    Атрибуты:
        name: Название места
        is_published: Флаг публикации
        created_at: Дата создания
    """

    name = models.CharField(
        max_length=256,
        verbose_name='Название места'
    )

    class Meta:
        """Мета-класс для модели Location."""

        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'

    def __str__(self) -> str:
        return self._truncate_str(self.name)


class Post(PublishedCreatedModel):
    """Основная модель публикаций (постов).

    Атрибуты:
        title: Заголовок публикации
        text: Текст публикации
        pub_date: Дата и время публикации
        author: Автор публикации
        location: Привязка к местоположению
        category: Привязка к категории
        is_published: Флаг публикации
        created_at: Дата создания
    """

    title = models.CharField(
        max_length=256,
        verbose_name='Заголовок',
    )
    text = models.TextField(verbose_name='Текст')
    pub_date = models.DateTimeField(
        verbose_name='Дата и время публикации',
        help_text=(
            'Если установить дату и время в будущем — '
            'можно делать отложенные публикации.'),
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор публикации',
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Местоположение',
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Категория',
    )
    image = models.ImageField(
        'Изображение',
        upload_to='posts_images/',
        blank=True,
    )

    class Meta:
        """Мета-класс для модели Post."""

        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'
        ordering = ['-pub_date']
        default_related_name = 'posts'

    def __str__(self) -> str:
        return self._truncate_str(self.title)


class Comment(models.Model):
    """Класс для комментариев."""

    text = models.TextField('Текст комментария')
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )
    is_published = models.BooleanField(default=True)

    class Meta:
        """Мета-класс."""

        ordering = ('created_at',)
        verbose_name = 'комментарий'
        verbose_name_plural = 'Комментарии'
        default_related_name = 'comments'

    def __str__(self):
        return f'Комментарий {self.author} к посту {self.post}'
