from django.urls import path
from .views import TradeSearchAPIView

app_name = 'trades'

urlpatterns = [
    path('search/', TradeSearchAPIView.as_view(), name='search'),
]
