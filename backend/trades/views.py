from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.pagination import PageNumberPagination
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework import generics, status

from django.db.models import Q
from .models import Trade
from .serializers import TradeSerializer, TradeDetailSerializer, TradeSearchSerializer
from .permissions import IsOwnerOrReadOnly  # 1. 권한 가져오기 (게시글 삭제를 위함)
from math import ceil

from django.shortcuts import get_object_or_404

class TradePagination(PageNumberPagination):
    page_size = 2                   # 한 페이지당 개수 (size를 요청 안 했을 경우, 한 페이지당 개수)
    page_query_param = "page"         # ?page=1
    page_size_query_param = "size"    # ?size=20 (size 요청이 왔을 경우, 한 페이지당 개수)
    max_page_size = 100               # ?size=500 (size 요청이 너무 크면 최댓값 제한)
    
    def get_paginated_response(self, data):
        # 클라이언트가 요청한 size 값이 있을 경우 적용
        page_size = self.page_size  # 기본값을 설정
        if self.page_size_query_param in self.request.query_params:
            size = self.request.query_params.get(self.page_size_query_param)
            try:
                # size가 숫자라면 page_size로 적용
                page_size = min(int(size), self.max_page_size)  # 최대 페이지 크기로 제한
            except ValueError:
                pass  # 잘못된 값이 들어올 경우 기본 page_size 유지
        total_pages = ceil(self.page.paginator.count / float(page_size)) # 전체 데이터 수를 바탕으로 총 페이지 수 계산

        # 기존 응답에 'total_pages'를 추가
        return Response({
            'count': self.page.paginator.count,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'total_pages': total_pages,  # 총 페이지 수 추가
            'results': data
        })


class TradeSearchAPIView(APIView):
    def get(self, request):
        queryset = Trade.objects.select_related('book', 'user')

        # =====================
        # 🔍 검색 (제목 / 내용 / 도서명)
        # =====================
        search = request.query_params.get("search")
        searchType = request.query_params.get("searchType", "title")

        if search:
            if searchType == "title":
                queryset = queryset.filter(title__icontains=search)     # icontains -> 대소문자 구분없이 값이 포함되어있는가?
            elif searchType == "content":
                queryset = queryset.filter(content__icontains=search)
            elif searchType == "book":
                queryset = queryset.filter(book__title__icontains=search)
            elif searchType == "isbn":  # 특정도서 검색 대신 isbn(유니크 키) 대체
                queryset = queryset.filter(book__isbn__icontains=search)

        # =====================
        # 🔞 성인 도서 필터
        # =====================
        # 로그인한 사용자 정보 가져오기
        user = request.user

        # 기본값: 성인 도서 제외
        exclude_adult = True

        if user.is_authenticated:
            if user.age is not None and user.age >= 20:     # 나이가 있고, 20세 이상인 경우만 성인 가능성 열어둠
                adult_param = request.query_params.get("adult")
                if adult_param == "true":
                    exclude_adult = False

        if exclude_adult:   # 성인 도서 제외가 필요한 경우
            queryset = queryset.filter(book__adult=False)

        # =====================
        # 🏷 판매 유형
        # =====================
        saleTypes = request.query_params.getlist("saleType")
        if saleTypes:
            queryset = queryset.filter(sale_type__in=saleTypes)

        # =====================
        # 📦 거래 상태 (기본: 판매중)
        # =====================
        # '거래 가능만 보기' 버튼 생성 : 체크 시 available만, 체크 안 할 시 'available', 'reserved', 'sold' 전부 다
        status = request.query_params.get("status")
        if status == "available":
            queryset = queryset.filter(status="available")

        # =====================
        # 📍 거래 지역
        # =====================
        regions = request.query_params.getlist("region")

        if regions:
            queryset = queryset.filter(region__in=regions)


        # =====================
        # 💰 가격 범위
        # =====================
        min_price = request.query_params.get("min_price")
        max_price = request.query_params.get("max_price")

        if min_price:   # min_price가 있다면
            try:
                queryset = queryset.filter(price__gte=int(min_price))
            except (ValueError, TypeError):
                pass

        if max_price:   # max_price가 있다면
            try:
                queryset = queryset.filter(price__lte=int(max_price))
            except (ValueError, TypeError):
                pass
            
        # =====================
        # 🔃 정렬
        # =====================
        ordering = request.query_params.get("ordering", "-created_at")
        if ordering in ["created_at", "-created_at", "price", "-price"]:
            queryset = queryset.order_by(ordering)

            
        # =====================
        # 📄 페이지네이션
        # =====================
        paginator = TradePagination()
        page = paginator.paginate_queryset(queryset, request)    # 쿼리셋을 페이지네이션 적용 (현재 페이지에 해당하는 데이터만 반환)
        serializer = TradeSearchSerializer(page, many=True)      # 페이지네이션된 데이터를 직렬화 (BookSearchSerializer 사용)
        return paginator.get_paginated_response(serializer.data) # 페이지네이션된 응답 반환



# generices를 쓰지 않고 기본 APIView 만 썼으면 머리는 좋아지나 효율이 안좋아질뻔;;
# 여기엔 DRF가 미리 만들어둔 클래스가 많음
# 아쉽게도 rest-framework에 있는게 아니네
# class TradeListCreateView(generics.ListCreateAPIView):
class TradeListCreateView(ListCreateAPIView):
    """게시글 목록 조회 및 등록"""
    # GET, POST 요청만 받을 수 있음
    # 최신 생성 글부터 확인
    queryset = Trade.objects.all().order_by('-created_at')
    serializer_class = TradeSerializer
    permission_classes = [IsAuthenticatedOrReadOnly] # 조회는 누구나, 등록은 로그인 유저만
    pagination_class = TradePagination

    def perform_create(self, serializer):
        # 평점 등록 때처럼, 로그인한 유저를 판매자로 강제 지정!
        serializer.save(user=self.request.user)


# class TradeDetailView(generics.RetrieveUpdateDestroyAPIView):
class TradeDetailView(RetrieveUpdateDestroyAPIView):
    """게시글 상세 조회, 수정, 삭제"""
    # GET, PUT, PATCH, DELETE 요청 받을 수 있음 (POST X)
    queryset = Trade.objects.all()
    serializer_class = TradeDetailSerializer
    # permission_classes = [IsAuthenticatedOrReadOnly]
    # 2. 권한 변경: 로그인 여부만 체크하는 게 아니라 "본인 확인"까지 함
    # django rest-framework 에서는 작성자 본인 확인 기능까지는 제공하지 않기에 permissions.py
    # 에서 본인 확인이 필요함
    permission_classes = [IsOwnerOrReadOnly]
    # urls.py에서 variable routing으로 <int:id>를 사용했기에 id를 사용해서
    # 글을 찾겠다는 뜻
    lookup_field = 'id'
    # [조회] GET 요청이 오면 이 함수가 실행됨
    # HTTP method 와 함수의 연결 관계
    # 1. GET : retrieve
    # 2. PUT : update
    # 3. PATCH : partial_update
    # 4. DELETE : destroy
    def retrieve(self, request, *args, **kwargs):
        # 1. URL의 id값으로 게시글 객체를 가져옵니다.
        instance = self.get_object()
        # 2. 조회수를 1 증가시키고 저장합니다.
        instance.view_count += 1
        instance.save()
        
        # 3. 상세 페이지용 시리얼라이저에 객체를 넣어 데이터를 만듭니다.
        serializer = self.get_serializer(instance)
        
        # 4. 최종 데이터를 응답합니다.
        return Response(serializer.data)
    # [삭제] DELETE 요청이 오면? 
    # 우리가 따로 안 적어도 부모 클래스(DestroyAPIView)가 
    # 내부적으로 'destroy' 함수를 실행해서 DB에서 싹 지워줍니다.

