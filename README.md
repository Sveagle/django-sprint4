Blogicum Platform

A Django-based blog platform with user profiles, post management, comments, and category organization.
Features
Core Functionality
  
    User Authentication: Registration, login, and profile management
  
    Post Management: Create, edit, and publish blog posts
  
    Categories: Organize posts into published categories
  
    Comments: Add and manage comments on posts
  
    Pagination: Efficient browsing through content

User Roles

    Authors: Full control over their own posts and comments
  
    Readers: View published content and comment on posts
  
    Anonymous Users: Browse published posts only

Content Moderation

    Posts require publication approval
  
    Category-based content filtering
  
    Comment management by authors

Installation

  Clone the repository

git clone <repository-url>
cd django-sprint4

Create virtual environment
  
  python -m venv venv
  source venv/bin/activate  # Linux/Mac
  or
  venv\Scripts\activate  # Windows

Install dependencies

  pip install -r requirements.txt

Database setup

  python manage.py migrate

Create superuser

  python manage.py createsuperuser

Run development server

  python manage.py runserver

Key Components

Models

    Post: Blog posts with publication status and metadata

    Category: Content categorization with publication control

    Comment: User comments on posts

    Location: Post location information

Mixins

    PublishedPostsMixin: Common post operations and filtering

    CommentMixin: Comment-related functionality reuse

Views

    IndexView: Homepage with published posts

    PostDetailView: Individual post viewing

    CategoryPostsView: Posts by category

    ProfileView: User profile with their posts

    CommentUpdateView: Comment editing

    CommentDeleteView: Comment deletion
