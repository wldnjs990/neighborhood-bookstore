from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Book
from .serializers import BookSearchSerializer
from django.db.models import Q

# Create your views here.

class BookSearchAPIView(APIView):
    def get(self, request):
        queryset = Book.objects.all()

        # 🔍 제목 + 저자 검색
        search = request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(author__icontains=search)
            )

        # 🏷️ 카테고리 검색
        category = request.query_params.get('category')
        if category:
            queryset = queryset.filter(category__name=category)

        # 🔞 성인 도서 필터
        adult = request.query_params.get('adult')
        if adult is not None:
            queryset = queryset.filter(adult=(adult.lower() == 'true'))

        serializer = BookSearchSerializer(queryset, many=True)
        return Response(serializer.data)
