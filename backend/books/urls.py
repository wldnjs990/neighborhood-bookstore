# books/urls.py
from django.urls import path
from .views import BookSearchAPIView

appname = 'books'
urlpatterns = [
    path('search/', BookSearchAPIView.as_view(), name='search'),
]