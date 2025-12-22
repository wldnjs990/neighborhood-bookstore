from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Q

from .models import Trade
from .serializers import TradeSearchSerializer


class TradeSearchAPIView(APIView):
    def get(self, request):
        queryset = Trade.objects.select_related('book', 'user')

        # =====================
        # 🔍 검색 (제목 / 내용 / 도서명)
        # =====================
        search = request.query_params.get("search")
        searchType = request.query_params.get("search_type", "title")

        if search:
            if searchType == "title":
                queryset = queryset.filter(title__icontains=search)
            elif searchType == "content":
                queryset = queryset.filter(content__icontains=search)
            elif searchType == "book":
                queryset = queryset.filter(book__title__icontains=search)

        # =====================
        # 🏷 판매 유형
        # =====================
        saleTypes = request.query_params.getlist("sale_type")
        print(saleTypes)
        if saleTypes:
            queryset = queryset.filter(sale_type__in=saleTypes)

        # =====================
        # 📦 거래 상태 (기본: 판매중)
        # =====================
        status = request.query_params.get("status", "available")
        if status:
            queryset = queryset.filter(status=status)

        # =====================
        # 📍 거래 지역
        # =====================
        regions = request.query_params.getlist("regions")

        if regions:
            region_q = Q()
            for r in regions:
                region_q |= Q(region__icontains=r)

            queryset = queryset.filter(region_q)

        # =====================
        # 💰 가격 범위
        # =====================
        min_price = request.query_params.get("min_price")
        max_price = request.query_params.get("max_price")

        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)

        # =====================
        # 📚 특정 도서
        # =====================
        book_id = request.query_params.get("book_id")
        if book_id:
            queryset = queryset.filter(book_id=book_id)

        # =====================
        # 📦 거래 상태 (체크박스 다중 선택)
        # =====================
        statuses = request.query_params.getlist("status")

        if statuses:
            queryset = queryset.filter(status__in=statuses)
            
        # =====================
        # 🔃 정렬
        # =====================
        ordering = request.query_params.get("ordering", "-created_at")
        if ordering in ["created_at", "-created_at", "price", "-price"]:
            queryset = queryset.order_by(ordering)

        serializer = TradeSearchSerializer(queryset, many=True)
        return Response(serializer.data)