from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Q

from .models import Book
from .serializers import BookSearchSerializer


class BookSearchAPIView(APIView):
    def get(self, request):
        queryset = Book.objects.all()

        # =====================
        # 🔍 제목 / 저자 검색 (라디오 버튼)
        # =====================
        search_type = request.query_params.get("search_type")  # title | author
        search = request.query_params.get("search")

        if search and search_type:
            if search_type == "title":
                queryset = queryset.filter(title__icontains=search)
            elif search_type == "author":
                queryset = queryset.filter(author__icontains=search)

        # =====================
        # 🏷️ 카테고리 필터 (체크박스, AND 결합)
        # =====================
        categories = request.query_params.getlist("categories")
        # 예: ["과학", "학습지"]

        if categories:
            queryset = queryset.filter(category__name__in=categories)

        # =====================
        # 🔞 성인 도서 필터
        # =====================
        adult = request.query_params.get("adult")
        # adult = "true" | "false" | None

        if adult is not None:
            queryset = queryset.filter(adult=(adult.lower() == "true"))

        serializer = BookSearchSerializer(queryset, many=True)
        return Response(serializer.data)