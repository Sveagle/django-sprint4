"""Формы приложения blog."""
from django import forms
from blog.models import Post, Comment


class PostForm(forms.ModelForm):
    """Формы для постов."""

    class Meta:
        """Мета-класс формы Post."""

        model = Post
        fields = ('title', 'text', 'category', 'location', 'image', 'pub_date')
        widgets = {
            'pub_date': forms.DateTimeInput(attrs={'type': 'datetime-local'})
        }


class CommentForm(forms.ModelForm):
    """Форма для комментариев."""

    class Meta:
        """Мета-класс формы Comment."""

        model = Comment
        fields = ('text',)
