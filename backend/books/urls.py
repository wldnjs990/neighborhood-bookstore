from django.urls import path
from . import views
# from .views import BookSearchAPIView, BestSellerAPIView, BookRatingView

app_name = 'books'

urlpatterns = [
    path('', views.book_list),
    path('<int:id>/', views.book_detail),
    path('<int:id>/bookmarks/', views.book_mark),
    path('<int:id>/rating/', views.BookRatingView.as_view(), name='book_rating'), # 평점 등록 API 추가
    path('bestseller/', views.BestSellerAPIView.as_view(), name='best_seller'),
    path('search/', views.BookSearchAPIView.as_view(), name='search'),
    path('bookmarked/', views.BookmarkedBooksView.as_view(), name='bookmarked_books'),
    path('autocomplete/', views.BookAutocompleteAPIView.as_view()),
]
