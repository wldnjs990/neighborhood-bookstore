from django.urls import path
from .views import TradeListCreateView, TradeDetailView

app_name = 'trades'

urlpatterns = [
    # 게시글 목록 및 등록: /api/trades/
    path('', TradeListCreateView.as_view(), name='trade_list_create'),
    # 게시글 상세, 수정, 삭제: /api/trades/<id>/
    path('<int:id>/', TradeDetailView.as_view(), name='trade_detail'),
]