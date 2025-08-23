"""View-классы приложения blog."""
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.db.models import QuerySet, Count
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils import timezone
from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, UpdateView
)

from blog.constants import POSTS_PER_PAGE
from blog.forms import CommentForm, PostForm
from blog.models import Comment, Category, Post


class PublishedPostsMixin:
    """Миксин для работы с постами."""

    def apply_common_annotations(self, queryset):
        """Применяет общие аннотации и select_related к queryset."""
        return queryset.select_related(
            'author', 'category', 'location'
        ).annotate(
            comment_count=Count('comments')
        )

    def filter_published_posts(self, queryset):
        """Фильтрует только опубликованные посты."""
        return queryset.filter(
            is_published=True,
            pub_date__lte=timezone.now(),
            category__is_published=True
        )

    def get_base_queryset(self):
        """Базовый QuerySet для всех постов с аннотациями."""
        queryset = Post.objects.all()
        queryset = self.apply_common_annotations(queryset)
        return queryset.order_by('-pub_date')

    def get_queryset(self):
        """Возвращает опубликованные посты (для ListView)."""
        queryset = self.get_base_queryset()
        return self.filter_published_posts(queryset)


class IndexView(PublishedPostsMixin, ListView):
    """Представление для отображения главной страницы с постами."""

    template_name = 'blog/index.html'
    paginate_by = POSTS_PER_PAGE


class PostDetailView(DetailView):
    """
    Представление для детального просмотра поста.

    Для автора поста отображает пост в любом статусе.
    Для других пользователей - только опубликованные посты.
    """

    model = Post
    template_name = 'blog/detail.html'
    pk_url_kwarg = 'post_id'

    def get_queryset(self):
        """
        Возвращает QuerySet в зависимости от прав пользователя.

        Returns:
            QuerySet: Все посты для автора, только опубликованные для других.
        """
        queryset = Post.objects.select_related(
            'category',
            'author',
            'location')
        if self.request.user.is_authenticated:
            post = get_object_or_404(Post, pk=self.kwargs['post_id'])
            if self.request.user == post.author:
                return queryset
        return queryset.filter(
            pub_date__lte=timezone.now(),
            is_published=True,
            category__is_published=True
        )

    def get_context_data(self, **kwargs):
        """
        Добавляет в контекст форму комментария и список комментариев.

        Returns:
            dict: Контекст данных для шаблона.
        """
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = self.object.comments.filter(
            is_published=True
        ).select_related(
            'author'
        ).order_by('created_at')

        return context


class CategoryPostsView(PublishedPostsMixin, ListView):
    """Представление для отображения постов определенной категории."""

    template_name = 'blog/category.html'
    context_object_name = 'post_list'
    paginate_by = POSTS_PER_PAGE

    def get_category(self) -> Category:
        """Возвращает опубликованную категорию по slug."""
        return get_object_or_404(
            Category,
            is_published=True,
            slug=self.kwargs['category_slug']
        )

    def get_queryset(self) -> QuerySet:
        """
        Возвращает опубликованные посты указанной категории.

        Returns:
            QuerySet: Посты отфильтрованные по категории.
        """
        queryset = super().get_queryset()
        category = self.get_category()
        return queryset.filter(category=category)

    def get_context_data(self, **kwargs) -> dict:
        """
        Добавляет информацию о категории в контекст.

        Returns:
            dict: Контекст данных для шаблона с информацией о категории.
        """
        context = super().get_context_data(**kwargs)
        context['category'] = self.get_category()
        return context


class PostCreateView(LoginRequiredMixin, CreateView):
    """Представление для создания нового поста."""

    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        """Устанавливает автора поста перед сохранением."""
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        """Возвращает URL для перенаправления после успешного создания."""
        return reverse(
            'blog:profile',
            kwargs={'username': self.request.user.username}
        )


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Представление для редактирования существующего поста."""

    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'

    def test_func(self):
        """Проверяет, является ли пользователь автором поста."""
        return self.get_object().author == self.request.user

    def handle_no_permission(self):
        """Обрабатывает случай, когда пользователь не проходит проверку."""
        if not self.request.user.is_authenticated:
            return redirect('login')

        post_id = self.kwargs.get('post_id')
        return redirect('blog:post_detail', post_id=post_id)

    def get_success_url(self):
        """Возвращает URL для перенаправления после успешного обновления."""
        return reverse('blog:post_detail', kwargs={'post_id': self.object.pk})


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Представление для удаления поста."""

    model = Post
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'

    def test_func(self):
        """Проверяет, является ли пользователь автором поста."""
        return self.get_object().author == self.request.user

    def get_context_data(self, **kwargs):
        """Добавляет форму с данными удаляемого поста в контекст."""
        context = super().get_context_data(**kwargs)
        context['form'] = PostForm(instance=self.object)
        return context

    def get_success_url(self):
        """Возвращает URL для перенаправления после успешного удаления."""
        return reverse('blog:profile',
                       kwargs={'username': self.request.user.username})


class CommentCreateView(LoginRequiredMixin, CreateView):
    """Создание комментария к посту."""

    model = Comment
    form_class = CommentForm

    def get_post_object(self):
        """Получаем пост для комментария."""
        return get_object_or_404(Post, pk=self.kwargs['post_id'])

    def form_valid(self, form):
        """Устанавливаем автора и пост комментария."""
        post_obj = self.get_post_object()
        form.instance.author = self.request.user
        form.instance.post = post_obj
        return super().form_valid(form)

    def get_success_url(self):
        """Возвращаем URL страницы поста."""
        post_obj = self.get_post_object()
        return reverse('blog:post_detail', kwargs={'post_id': post_obj.pk})


class CommentUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Представление для редактирования комментария."""

    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'

    def test_func(self):
        """Проверяет, является ли пользователь автором комментария."""
        return self.get_object().author == self.request.user

    def get_success_url(self):
        """Возвращает URL для перенаправления после успешного обновления."""
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': self.kwargs['post_id']}
        )


class CommentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Представление для удаления комментария."""

    model = Comment
    pk_url_kwarg = 'comment_id'
    template_name = 'blog/comment.html'

    def test_func(self):
        """Проверяет, является ли пользователь автором комментария."""
        return self.get_object().author == self.request.user

    def get_success_url(self):
        """Возвращает URL для перенаправления после успешного удаления."""
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': self.kwargs['post_id']}
        )


class ProfileView(PublishedPostsMixin, ListView):
    """Представление для отображения профиля пользователя с его постами."""

    template_name = 'blog/profile.html'
    context_object_name = 'posts'
    paginate_by = POSTS_PER_PAGE

    def get_profile_user(self):
        """Возвращает пользователя профиля."""
        return get_object_or_404(User, username=self.kwargs['username'])

    def get_queryset(self):
        """Возвращает посты пользователя."""
        user_profile = self.get_profile_user()
        queryset = user_profile.posts.all()

        queryset = self.apply_common_annotations(queryset)

        if self.request.user != user_profile:
            queryset = self.filter_published_posts(queryset)

        return queryset.order_by('-pub_date')

    def get_context_data(self, **kwargs):
        """Добавляет информацию о пользователе профиля в контекст."""
        context = super().get_context_data(**kwargs)
        context['profile'] = self.get_profile_user()
        return context


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    """Представление для редактирования профиля пользователя."""

    model = User
    form_class = UserChangeForm
    template_name = 'blog/user.html'

    def get_object(self, queryset=None):
        """Возвращает текущего пользователя для редактирования."""
        return self.request.user

    def get_success_url(self):
        """Возвращает URL для перенаправления после успешного обновления."""
        return reverse('blog:profile',
                       kwargs={'username': self.request.user.username})


class SignupView(CreateView):
    """Представление для регистрации нового пользователя."""

    form_class = UserCreationForm
    template_name = 'registration/registration_form.html'

    def get_success_url(self):
        """Возвращает URL для перенаправления после успешной регистрации."""
        return reverse('login')
