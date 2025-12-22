from django.urls import path
from . import views
from .views import BookSearchAPIView, BestSellerAPIView

app_name = 'books'

urlpatterns = [
    path('', views.book_list),
    path('<int:id>/', views.book_detail),
    path('<int:id>/bookmarks/', views.book_mark),
    path('bestseller/', BestSellerAPIView.as_view(), name='best_seller'),
    path('search/', BookSearchAPIView.as_view(), name='search'),
]
