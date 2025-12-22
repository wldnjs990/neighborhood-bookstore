from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q
from math import ceil

from .models import Book
from .serializers import BookSearchSerializer


class BookPagination(PageNumberPagination):
    page_size = 25                   # 한 페이지당 개수 (size를 요청 안 했을 경우, 한 페이지당 개수)
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
        # 전체 데이터 수를 바탕으로 총 페이지 수 계산
        total_pages = ceil(self.page.paginator.count / float(page_size))

        # 기존 응답에 'total_pages'를 추가
        return Response({
            'count': self.page.paginator.count,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'total_pages': total_pages,  # 총 페이지 수 추가
            'results': data
        })

class BookSearchAPIView(APIView):
    def get(self, request):
        # 전체 Book 객체를 조회 (기본 쿼리셋)
        queryset = Book.objects.all()

        # =====================
        # 🔍 검색 타입 (기본: 제목으로 검색)
        # =====================
        search_type = request.query_params.get("search_type", "title")  # 쿼리 파라미터에서 검색 타입을 가져옴 (기본값: 'title')
        search = request.query_params.get("search")                     # 쿼리 파라미터에서 검색어를 가져옴

        
        if search:
            if search_type == "title":
                queryset = queryset.filter(title__icontains=search)     # 제목에 검색어가 포함된 도서만 필터링
            elif search_type == "author":
                queryset = queryset.filter(author__icontains=search)    # 저자에 검색어가 포함된 도서만 필터링

        # =====================
        # 🏷️ 카테고리 (체크박스)
        # =====================
        categories = request.query_params.getlist("categories")         # 쿼리 파라미터에서 'categories' 값들(체크된 카테고리들)을 리스트로 받음
        categories = [int(ct) for ct in categories]
        if categories:
            queryset = queryset.filter(category__id__in=categories)   # 카테고리명이 목록에 포함된 도서만 필터링

        # =====================
        # 🔞 성인 도서 필터
        # =====================
        # 로그인한 사용자 정보 가져오기
        user = request.user
        if not user.is_authenticated:
            queryset = queryset.filter(adult=False)          # 로그인이 안 되어 있으면 성인 도서를 제외
        elif user.age < 20:
            queryset = queryset.filter(adult=False)          # 나이가 20세 미만이면 성인 도서를 제외
        else:
            adult_param = request.query_params.get("adult")  # 로그인한 유저가 성인일 경우, 성인 도서 필터링 (파라미터가 있으면 체크)
            if adult_param != "true":
                queryset = queryset.filter(adult=False)

        # =====================
        # 📄 페이지네이션
        # =====================
        paginator = BookPagination()
        page = paginator.paginate_queryset(queryset, request)    # 쿼리셋을 페이지네이션 적용 (현재 페이지에 해당하는 데이터만 반환)
        serializer = BookSearchSerializer(page, many=True)       # 페이지네이션된 데이터를 직렬화 (BookSearchSerializer 사용)
        return paginator.get_paginated_response(serializer.data) # 페이지네이션된 응답 반환

