from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.decorators import permission_classes # permission Decorators
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination

from django.shortcuts import get_object_or_404, get_list_or_404
from django.db.models import Q

from .services.recommand import BookRecommendationCandidate
from .services.ai_prompt import build_recommend_prompt
from .services.ai_client import llm_client
from .serializers import BookPreviewSerializer, BookDetailSerializer, BookSearchSerializer, BookBestSellerSerializer, BookRatingSerializer, BookAutocompleteSerializer, BookAIInputSerializer
from .models import Book, Bookmark, BookRating

from math import ceil


# drf spectacular 사용
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse
from drf_spectacular.types import OpenApiTypes
# Create your views here.

# 도서 메인
@api_view(['GET'])
def book_list(request):
    if request.method == 'GET':
        # 1. best_rank가 null인 데이터를 제외하고 (순위가 있는 것만)
        # 2. best_rank 기준 오름차순 정렬 (1, 2, 3...)
        # 3. 상위 10개만 슬라이싱
        queryset = Book.objects.filter(best_rank__isnull=False).order_by('best_rank')[:10]
        # 데이터가 없으면 자동으로 404를 일으키고, 있으면 리스트를 반환
        books = get_list_or_404(queryset)
        serializer = BookPreviewSerializer(books, many=True)
        return Response(serializer.data)


# 도서 상세
@extend_schema(
    responses=BookDetailSerializer,
    summary="도서 상세 조회"
)
@api_view(['GET'])
def book_detail(request, id):
    book = get_object_or_404(Book, pk=id)
    if request.method == 'GET':
        serializer = BookDetailSerializer(book, context={'request': request})
        return Response(serializer.data)


# 도서 북마크
# 테스트 방법 : /api/v1/books/1/bookmarks/ 에서 Header에 직접
# Authorization을 하고 POST 요청을 보내면 됨
# request body는 필요 없음
# TIP : swagger-ui url로 이동하여 실행 시 Authorize에 login할 사용자의
# Token 값을 집어넣기
@extend_schema(
    summary="도서 북마크 토글",
    description="인증된 사용자가 특정 도서를 북마크/해제합니다.",
    parameters=[
        OpenApiParameter(
            name="id",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.PATH,
            description="북마크할 도서 ID",
            required=True,
        ),
    ],
    request=None,  # ⭐ body 없음
    responses={
        200: OpenApiResponse(
            response={
                "type": "object",
                "properties": {
                    "is_bookmarked": {"type": "boolean"},
                    "message": {"type": "string"},
                },
            },
            description="북마크 처리 결과"
        )
    },
)
@api_view(['POST'])
@permission_classes([IsAuthenticated]) # 로그인한 사용자만 가능
def book_mark(request, id):
    book = get_object_or_404(Book, pk=id)
    user = request.user

    # 현재 사용자가 이 책을 북마크했는지 확인
    bookmark = Bookmark.objects.filter(user=user, book=book)

    if bookmark.exists():
        # 이미 있다면 삭제 (북마크 해제)
        bookmark.delete()
        return Response({'is_bookmarked': False, 'message': '북마크가 해제되었습니다.'})
    else:
        # 없다면 생성 (북마크 등록)
        Bookmark.objects.create(user=user, book=book)
        return Response({'is_bookmarked': True, 'message': '북마크가 등록되었습니다.'})


# 알고리즘 신 - 도서 검색
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
        total_pages = ceil(self.page.paginator.count / float(page_size)) # 전체 데이터 수를 바탕으로 총 페이지 수 계산

        # 기존 응답에 'total_pages'를 추가
        return Response({
            'count': self.page.paginator.count,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'total_pages': total_pages,  # 총 페이지 수 추가
            'results': data
        })


# 알고리즘 신 - 도서 검색
class BookSearchAPIView(APIView):
    # 중요
    # GET + query_params는 Serializer로 나오지 않음
    # OpenApiParameter로 직접 선언해야 함
    # Query params 전부 노출됨
    # 체크 박스 / enum 모두 표시
    @extend_schema(
        parameters=[
            OpenApiParameter("search", str, required=False),
            OpenApiParameter("searchType", str, required=False, enum=["title", "author"]),
            OpenApiParameter("categories", int, many=True, required=False),
            OpenApiParameter("adult", bool, required=False),
            OpenApiParameter("page", int, required=False),
            OpenApiParameter("size", int, required=False),
        ],
        responses=BookSearchSerializer,
        summary="도서 검색"
    )
    def get(self, request):
        # 전체 Book 객체를 조회 (기본 쿼리셋)
        queryset = Book.objects.all()

        # =====================
        # 🔍 검색 타입 (기본: 제목으로 검색)
        # =====================
        searchType = request.query_params.get("searchType", "title")  # 쿼리 파라미터에서 검색 타입을 가져옴 (기본값: 'title')
        search = request.query_params.get("search")                     # 쿼리 파라미터에서 검색어를 가져옴

        
        if search:
            if searchType == "title":
                queryset = queryset.filter(title__icontains=search)     # 제목에 검색어가 포함된 도서만 필터링
            elif searchType == "author":
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
        user = request.user

        # 기본값: 성인 도서 제외
        # exclude_adult = True

        if user.is_authenticated:
            # 나이가 있고, 20세 이상인 경우만 성인 가능성 열어둠
            if user.age is not None and user.age >= 20:
                adult_param = request.query_params.get("adult")
                if adult_param:
                    if adult_param in ("true", 1, "True"):
                        # exclude_adult = False
                        queryset = queryset.filter(adult=True)
                    elif adult_param in ("false", 0, "False"):
                        # exclude_adult = True
                        queryset = queryset.filter(adult=False)
            else:
                queryset = queryset.filter(adult=False)
        else:
            queryset = queryset.filter(adult=False)
                    

        # =====================
        # 📄 페이지네이션
        # =====================
        paginator = BookPagination()
        page = paginator.paginate_queryset(queryset, request)    # 쿼리셋을 페이지네이션 적용 (현재 페이지에 해당하는 데이터만 반환)
        serializer = BookSearchSerializer(page, many=True)       # 페이지네이션된 데이터를 직렬화 (BookSearchSerializer 사용)
        return paginator.get_paginated_response(serializer.data) # 페이지네이션된 응답 반환


# 베스트 셀러 도서 목록 확인 - 50개 단위
class BestSellerAPIView(APIView):
    def get(self, request):
        # 1. 순위 데이터가 있는 도서만 가져와서 순위순(오름차순) 정렬
        queryset = Book.objects.filter(best_rank__isnull=False).order_by('best_rank')

        # 2. 기존 BookPagination 클래스 그대로 사용
        paginator = BookPagination()
        
        # 3. [핵심] 검색(25개)과 달리 베스트셀러는 50개씩 보여주기 위해 인스턴스 설정만 변경
        paginator.page_size = 50 
        
        # 4. 페이지네이션 적용
        page = paginator.paginate_queryset(queryset, request)
        if page is not None:
            # 5. 기존 BookSearchSerializer 그대로 사용
            serializer = BookBestSellerSerializer(page, many=True)
            # 이미 구현하신 total_pages가 포함된 응답이 나갑니다.
            return paginator.get_paginated_response(serializer.data)

        # 데이터가 없을 경우를 대비한 기본 응답
        serializer = BookBestSellerSerializer(queryset, many=True)
        return Response(serializer.data)


class BookRatingView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="도서 평점 등록/수정",
        description="인증된 사용자가 도서에 평점을 남기거나 수정합니다.",
        parameters=[
            OpenApiParameter(
                name="id",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                description="평점을 등록할 도서 ID",
                required=True,
            )
        ],
        request=BookRatingSerializer,   # ⭐ score 여기서 등장
        responses={
            200: OpenApiResponse(
                response={
                    "type": "object",
                    "properties": {
                        "message": {"type": "string"},
                        "average_rating": {"type": "number"},
                        "rating_count": {"type": "integer"},
                    },
                },
                description="평점 등록 결과"
            )
        },
    )

    def post(self, request, id):
        # 1. 어떤 책인지 URL에서 가져옴
        book = get_object_or_404(Book, pk=id)
        
        # 2. 시리얼라이저에 데이터(score) 전달
        serializer = BookRatingSerializer(data=request.data)
        
        if serializer.is_valid():
            # 3. 여기서 중요! save()할 때 유저와 책 정보를 강제로 넣어줍니다.
            # 이러면 Vue에서 유저ID를 보낼 필요가 없어 보안에 안전합니다.
            rating, created = BookRating.objects.update_or_create(
                user=request.user,  # 요청을 보낸 로그인 유저
                book=book,          # URL로 들어온 책
                defaults={'score': serializer.validated_data['score']}
            )
            print(rating)
            print(created)
            
            # signal 사용할 때 발생할 수 있는 문제점 해결 완료 (회고 딸깍)
            # 이 순간 signals.py가 발동하여 Book 모델의 average_rating을 갱신합니다.
            book.refresh_from_db()

            return Response({
                "message": "등록 완료",
                "average_rating": book.average_rating,
                "rating_count": book.rating_count
            }, status=status.HTTP_200_OK)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


from rest_framework.generics import ListAPIView

# 프로필 페이지에서 조회할 수 있게 해줘야 함
class BookmarkedBooksView(ListAPIView):
    """사용자가 북마크한 도서 목록 조회"""
    serializer_class = BookPreviewSerializer
    permission_classes = [IsAuthenticated] # 로그인한 유저만 본인의 북마크 확인 가능

    def get_queryset(self):
        # 1. 현재 요청을 보낸 유저 정보를 가져옵니다.
        user = self.request.user
        
        # 2. Bookmark 모델을 통해 해당 유저가 북마크한 도서들만 필터링합니다.
        # Bookmark 모델에서 Book을 참조하는 related_name='bookmarks'를 활용합니다.
        return Book.objects.filter(bookmarks__user=user).order_by('-bookmarks__created_at')
    
# 중고거래에서 도서 선택 시 검색과 select하기
class BookAutocompleteAPIView(APIView):
    def get(self, request):
        # /api/books/autocomplete/?q=해 => request.query_params == {'q': '해'} => q = '해' : 자동 파싱
        q = request.query_params.get('q', '')

        queryset = Book.objects.filter(
            title__icontains=q
        ).order_by('title')[:10]  # 🔥 10개 제한
        """
        1. SQL 코드
        SELECT *
        FROM books_book
        WHERE title LIKE '%해%
        ORDER BY title ASC
        LIMIT 10

        - title 순으로 오름차순 정렬
        - 10개만 보여줌
        - 스크롤 만들고 싶으면 [:20] 후에 프론트에서 10개만 보이게하면 스크롤 생김.
        """

        serializer = BookAutocompleteSerializer(queryset, many=True)
        return Response(serializer.data)
    
class BookRecommendAPIView(APIView):
    """
    도서 추천 API
    - 카테고리 선택 (다중)
    - 사용자 요청 프롬프트
    - User.book_mbti → BookMBTI.info 자동 반영
    """
    permission_classes = [IsAuthenticatedOrReadOnly]
    

    def post(self, request):
        # print("====== USER DEBUG ======")
        # print("user:", request.user)
        # print("is_authenticated:", request.user.is_authenticated)
        # print("book_mbti:", getattr(request.user, "book_mbti", None))
        # print("====== END USER DEBUG ======")

        # 1️⃣ 요청 데이터
        category_ids = request.data.get("category_ids", [])
        user_prompt = request.data.get("user_prompt", "").strip()

        # 2️⃣ 추천 후보 50권
        selector = BookRecommendationCandidate(
            user=request.user,
            category_ids=category_ids
        )
        candidate_books = selector.get_top_50()
        # print("====== RECOMMEND DEBUG ======")
        # for i, book in enumerate(candidate_books, start=1):
        #     print(
        #         f"{i:02d}. "
        #         f"title={book.title} | "
        #         f"sales_point={book.sales_point} | "
        #         f"popularity={round(book.popularity_score, 4)} | "
        #         f"trend_boost={book.trend_boost} | "
        #         f"review_boost={book.review_boost} | "
        #         f"final_score={round(book.final_score, 4)} | "
        #     )
        # print("====== END DEBUG ======")

        # 3️⃣ BookMBTI 고정 프롬프트
        mbti_info_prompt = ""
        if request.user.is_authenticated and request.user.book_mbti:
            mbti_info_prompt = request.user.book_mbti.info

        print("====== MBTI PROMPT ======")
        if request.user.is_authenticated and request.user.book_mbti:
            print(request.user.book_mbti.code)
            print(request.user.book_mbti.info)
        else:
            print("NO MBTI")
        print("====== END MBTI ======")

        # 4️⃣ AI 입력용 도서 데이터
        books_payload = BookAIInputSerializer(
            candidate_books,
            many=True
        ).data

        # 🔀 AI 편향 방지용 셔플 (중요!)
        import random
        books_payload = list(books_payload)
        random.shuffle(books_payload)
        print("===== SHUFFLED CANDIDATES =====")
        for b in books_payload[:10]:
            print(b["title"])
        print("===== END =====")

        # print("====== BOOKS PAYLOAD SAMPLE ======")
        # for book in books_payload[:3]:
        #     print(book)
        # print(f"... total books = {len(books_payload)}")
        # print("====== END PAYLOAD ======")

        # 5️⃣ 프롬프트 생성
        prompt = build_recommend_prompt(
            mbti_info=mbti_info_prompt,
            user_prompt=user_prompt,
            books_payload=books_payload
        )

        # print("====== FINAL PROMPT ======")
        # print(prompt)
        # print("====== PROMPT LENGTH ======")
        # print(len(prompt))
        # print("====== END PROMPT ======")

        # 6️⃣ AI 호출
        result = llm_client.recommend_books(prompt)

        return Response(result)
    
        # 50권 호출 확인용 더미 return
        # return Response({
        #     "candidate_count": len(candidate_books),
        #     "candidates": [
        #         {
        #             "id": book.id,
        #             "title": book.title,
        #             "category" : book.category.id,
        #             "description" : book.description,
        #             "sales_point": book.sales_point,
        #             "best_rank": book.best_rank,
        #             "customer_review_rank": book.customer_review_rank,
        #             "pub_date": book.pub_date,
        #             "adult": book.adult,
        #         }
        #         for book in candidate_books
        #     ]
        # })