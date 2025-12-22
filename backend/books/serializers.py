from rest_framework import serializers
from .models import Book


# 1. 베스트셀러/일반 목록용 (북마크 정보 없음)
class BookPreviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ('id', 'best_rank', 'cover', 'title', 'customer_review_rank')      


# 2. 도서 상세 페이지용 (모든 정보 + 북마크 여부 포함)
class BookDetailSerializer(serializers.ModelSerializer):
    # DB 필드엔 없지만 응답에는 포함될 가상 필드
    is_bookmarked = serializers.SerializerMethodField()

    def get_is_bookmarked(self, obj):
        # 뷰에서 전달된 request 객체를 가져옵니다.
        request = self.context.get('request')
        
        # 로그인하지 않은 유저라면 북마크는 항상 False
        if not request or not request.user.is_authenticated:
            return False
            
        # 해당 유저가 이 도서(obj)를 북마크했는지 DB에서 확인
        # Bookmark 클래스에서 Book을 외래키로 참조 (북마크에서 도서 찾기) - related_name='bookmarks'
        # 이 도서를 참조하고 있는 북마크들의 목록을 가져오기
        # 그 중에서 지금 로그인한 유저가 만든 것만 골라내기 
        return obj.bookmarks.filter(user=request.user).exists()

    class Meta:
        model = Book
        fields = ('id', 'best_rank', 'cover', 'title', 'customer_review_rank', 'is_bookmarked')


# 4. 알고리즘 신 (검색)
class BookSearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = [
            "id",
            "title",
            "author",
            "category",
            "adult",
        ]


# 3. 베스트 셀러 목록들
class BookBestSellerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = [
            "id",
            "title",
            "author",
            "category",
            "adult",
            'best_rank',
        ]
