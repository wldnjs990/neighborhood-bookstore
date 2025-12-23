from rest_framework import serializers
from .models import Book, BookRating
# accounts 앱에 이미 정의된 UserSerializer를 가져옵니다.
from accounts.serializers import UserSerializer

# 1. 베스트셀러/일반 목록용 (북마크 정보 없음)
class BookPreviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ('id', 'best_rank', 'cover', 'title', 'customer_review_rank', 'adult')      


# 도서 평점을 위한 serializer
class BookRatingSerializer(serializers.ModelSerializer):
    # 유저와 책은 '읽기 전용'으로 설정해서 Vue가 이 데이터를 조작하지 못하게 합니다.
    user = serializers.ReadOnlyField(source='user.nickname') # 유저 닉네임을 보여주고 싶다면
    book = serializers.ReadOnlyField(source='book.title')

    class Meta:
        model = BookRating
        fields = ['score', 'user', 'book']


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
        fields = ('id', 'best_rank', 'cover', 'title', 'customer_review_rank', 'best_rank', 'rating_count', 'average_rating', 'is_bookmarked', 'adult')


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


# 중고거래 페이지용
class BookTradeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ('id', 'cover', 'title', 'customer_review_rank', 'adult', 'price_standard', 'category')  

