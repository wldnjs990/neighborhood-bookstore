from django.urls import path
from . import views
from .views import BookSearchAPIView

app_name = 'books'

urlpatterns = [
    path('books/', views.book_list),
    path('books/<int:id>/', views.book_detail),
    path('books/<int:id>/bookmarks/', views.book_mark),
    # path('books/bestseller/', views.book_bestseller_list),
    path('search/', BookSearchAPIView.as_view(), name='search'),
]
