"""URL конфугурация приложения blog."""
from django.urls import include, path
from blog import views

app_name = 'blog'

posts_urls = [
    path('create/',
         views.PostCreateView.as_view(),
         name='create_post'),
    path('<int:post_id>/',
         views.PostDetailView.as_view(),
         name='post_detail'),
    path('<int:post_id>/edit/',
         views.PostUpdateView.as_view(),
         name='edit_post'),
    path('<int:post_id>/delete/',
         views.PostDeleteView.as_view(),
         name='delete_post'),
    path('<int:post_id>/comment/',
         views.CommentCreateView.as_view(),
         name='add_comment'),
]

comments_urls = [
    path('<int:comment_id>/edit/',
         views.CommentUpdateView.as_view(),
         name='edit_comment'),
    path('<int:comment_id>/delete/',
         views.CommentDeleteView.as_view(),
         name='delete_comment'),
]

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path(
        'category/<slug:category_slug>/',
        views.CategoryPostsView.as_view(),
        name='category_posts'),
    path('auth/registration/',
         views.SignupView.as_view(),
         name='registration'),
    path('profile/edit_profile/',
         views.ProfileUpdateView.as_view(),
         name='edit_profile'),
    path('profile/<str:username>/',
         views.ProfileView.as_view(),
         name='profile'),
    path('posts/', include(posts_urls)),
    path('posts/<int:post_id>/comments/', include(comments_urls)),
]
