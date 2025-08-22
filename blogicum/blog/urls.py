"""URL конфугурация приложения blog."""
from django.urls import path
from .views import (
    IndexView, PostCreateView, PostDetailView, CategoryPostsView,
    SignupView, ProfileView, PostUpdateView, PostDeleteView,
    CommentCreateView, CommentUpdateView, CommentDeleteView,
    ProfileUpdateView
)

app_name = 'blog'

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('posts/<int:post_id>/', PostDetailView.as_view(), name='post_detail'),
    path(
        'category/<slug:category_slug>/',
        CategoryPostsView.as_view(),
        name='category_posts'
    ),
    path('auth/registration/', SignupView.as_view(), name='registration'),
    path(
        'profile/edit_profile/',
        ProfileUpdateView.as_view(),
        name='edit_profile'
    ),
    path('profile/<str:username>/', ProfileView.as_view(), name='profile'),
    path('posts/create/', PostCreateView.as_view(), name='create_post'),
    path(
        'posts/<int:post_id>/edit/',
        PostUpdateView.as_view(),
        name='edit_post'
    ),
    path(
        'posts/<int:post_id>/delete/',
        PostDeleteView.as_view(),
        name='delete_post'
    ),
    path('posts/<int:post_id>/comment/',
         CommentCreateView.as_view(),
         name='add_comment'),
    path(
        'posts/<int:post_id>/comments/<int:comment_id>/edit_comment/',
        CommentUpdateView.as_view(),
        name='edit_comment'
    ),
    path(
        'posts/<int:post_id>/comments/<int:comment_id>/delete/',
        CommentDeleteView.as_view(),
        name='delete_comment'
    ),
]
