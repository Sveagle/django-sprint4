"""Формы приложения blog."""
from django import forms

from blog.models import Comment, Post


class PostForm(forms.ModelForm):
    """Формы для постов."""

    class Meta:
        """Мета-класс формы Post."""

        model = Post
        exclude = ('author', 'created_at',)
        widgets = {
            'pub_date': forms.DateTimeInput(
                attrs={'type': 'datetime-local'},
                format='%Y-%m-%dT%H:%M'),
            'is_published': forms.CheckboxInput(
                attrs={'class': 'form-check-input'}
            )
        }


class CommentForm(forms.ModelForm):
    """Форма для комментариев."""

    class Meta:
        """Мета-класс формы Comment."""

        model = Comment
        fields = ('text',)

        widgets = {
            'text': forms.Textarea(attrs={
                'cols': 40,
                'rows': 4,
                'placeholder': 'Введите ваш комментарий...',
                'class': 'form-textarea',
                'style': 'resize: vertical;'
            })
        }
