"""View-классы приложения blog."""
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.db.models import QuerySet, Count
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, UpdateView
)

from blog.constants import POSTS_PER_PAGE
from blog.forms import CommentForm, PostForm
from blog.models import Comment, Category, Post


class PublishedPostsMixin:
    """Миксин для получения только опубликованных постов."""

    def get_queryset(self) -> QuerySet:
        """
        Возвращает QuerySet с опубликованными постами.

        Returns:
            QuerySet: Посты, отфильтрованные по дате публикации,
                     статусу публикации и опубликованной категории,
                     с аннотацией количества комментариев.
        """
        return Post.objects.select_related(
            'category', 'author', 'location'
        ).filter(
            pub_date__lte=timezone.now(),
            is_published=True,
            category__is_published=True
        ).annotate(comment_count=Count('comments')).order_by('-pub_date')


class IndexView(PublishedPostsMixin, ListView):
    """Представление для отображения главной страницы с постами."""

    template_name = 'blog/index.html'
    context_object_name = 'post_list'
    paginate_by = POSTS_PER_PAGE


class PostDetailView(DetailView):
    """
    Представление для детального просмотра поста.

    Для автора поста отображает пост в любом статусе.
    Для других пользователей - только опубликованные посты.
    """

    model = Post
    template_name = 'blog/detail.html'
    context_object_name = 'post'
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
            is_published=True).order_by('created_at')
        return context


class CategoryPostsView(PublishedPostsMixin, ListView):
    """Представление для отображения постов определенной категории."""

    template_name = 'blog/category.html'
    context_object_name = 'post_list'
    paginate_by = POSTS_PER_PAGE

    def get_queryset(self) -> QuerySet:
        """
        Возвращает опубликованные посты указанной категории.

        Returns:
            QuerySet: Посты отфильтрованные по категории.
        """
        queryset = super().get_queryset()
        category = get_object_or_404(Category, is_published=True,
                                     slug=self.kwargs['category_slug'])
        return queryset.filter(category=category)

    def get_context_data(self, **kwargs) -> dict:
        """
        Добавляет информацию о категории в контекст.

        Returns:
            dict: Контекст данных для шаблона с информацией о категории.
        """
        context = super().get_context_data(**kwargs)
        context['category'] = get_object_or_404(
            Category,
            is_published=True,
            slug=self.kwargs['category_slug']
        )
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
        return reverse_lazy('blog:profile',
                            kwargs={'username': self.request.user.username})


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
        return reverse_lazy('blog:post_detail',
                            kwargs={'post_id': self.object.pk})


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Представление для удаления поста."""

    model = Post
    template_name = 'blog/detail.html'
    pk_url_kwarg = 'post_id'

    def test_func(self):
        """Проверяет, является ли пользователь автором поста."""
        return self.get_object().author == self.request.user

    def get_success_url(self):
        """Возвращает URL для перенаправления после успешного удаления."""
        return reverse_lazy('blog:profile',
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
        form.instance.is_published = True
        return super().form_valid(form)

    def get_success_url(self):
        """Возвращаем URL страницы поста."""
        post_obj = self.get_post_object()
        return reverse_lazy('blog:post_detail',
                            kwargs={'post_id': post_obj.pk})


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
        return reverse_lazy('blog:post_detail',
                            kwargs={'post_id': self.kwargs['post_id']})


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
        return reverse_lazy('blog:post_detail',
                            kwargs={'post_id': self.kwargs['post_id']})


class ProfileView(ListView):
    """Представление для отображения профиля пользователя с его постами."""

    template_name = 'blog/profile.html'
    context_object_name = 'posts'
    paginate_by = POSTS_PER_PAGE

    def get_queryset(self):
        """Возвращает посты пользователя."""
        user_profile = get_object_or_404(User,
                                         username=self.kwargs['username'])
        queryset = user_profile.posts.all().annotate(
            comment_count=Count('comments'))

        if self.request.user != user_profile:
            queryset = queryset.filter(
                is_published=True,
                pub_date__lte=timezone.now(),
                category__is_published=True
            )

        return queryset.order_by('-pub_date')

    def get_context_data(self, **kwargs):
        """Добавляет информацию о пользователе профиля в контекст."""
        context = super().get_context_data(**kwargs)
        context['profile'] = get_object_or_404(
            User,
            username=self.kwargs['username'])
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
        return reverse_lazy('blog:profile',
                            kwargs={'username': self.request.user.username})


class SignupView(CreateView):
    """Представление для регистрации нового пользователя."""

    form_class = UserCreationForm
    template_name = 'registration/registration_form.html'
    success_url = reverse_lazy('login')
