"""Backend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.views.defaults import page_not_found
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from Backend.books import views
from Backend.books.views import AuthorView, BookView, ReviewView, UserDetailsView, NotFoundView, custom404


#method not allowed kai random url 405
urlpatterns = [
    path('admin/', admin.site.urls),
    path('user-details/', UserDetailsView.as_view(), name='user-details'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('authors/', AuthorView.as_view(), name='author-list'),
    path('authors/<int:author_id>/', AuthorView.as_view(), name='author-detail'),
    path('books/', BookView.as_view(), name='book-list'),
    path('author/<int:author_id>/books/', BookView.as_view(), name='book-list'),
    path('author/<int:author_id>/books/<int:book_id>/', BookView.as_view(), name='book-detail'),
    path('reviews/', ReviewView.as_view(), name='review-list'),
    path('author/<int:author_id>/book/<int:book_id>/reviews', ReviewView.as_view(), name='review-detail'),
    path('author/<int:author_id>/book/<int:book_id>/reviews/<int:review_id>/', ReviewView.as_view(), name='review-detail'),

    path('<path:path>', views.method_not_allowed),
]
