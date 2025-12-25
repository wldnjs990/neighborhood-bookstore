# books/serializers.py
from rest_framework import serializers
from .models import Book, BookRating, Category
# accounts 앱에 이미 정의된 UserSerializer를 가져옵니다.
from accounts.serializers import UserSerializer


# 도서의 카테고리를 상세하게 보여주기 위한 serializer
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']


# 1. 베스트셀러/일반 목록용 (북마크 정보 없음)
class BookPreviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = '__all__'     


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
    # 방법 1 : serializers.SerializerMethodField() 작성
    trades = serializers.SerializerMethodField()
    category = CategorySerializer()
    
    # # 방법 2 : 이 책과 연관된 중고거래 목록
    # trades = TradePreviewSerializer(
    #     many=True,
    #     read_only=True,
    #     source='trades'   # related_name
    # )
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

    def get_trades(self, obj):
        """
        이 책(obj)에 등록된 중고거래 목록을 가져온다
        """
        # 상세 정보에 관련된 중고 거래 목록을 확인해야 함
        from trades.models import Trade
        from trades.serializers import TradePreviewSerializer
        trades = Trade.objects.filter(book=obj).select_related('user')
        serializer = TradePreviewSerializer(trades, many=True)
        return serializer.data    

    class Meta:
        model = Book
        fields = '__all__'


# 4. 알고리즘 신 (검색)
class BookSearchSerializer(serializers.ModelSerializer):
    # 카테고리 serializer 추가 (이름 확인)
    category = CategorySerializer(read_only=True)
    class Meta:
        model = Book
        fields = '__all__'


# 3. 베스트 셀러 목록들
class BookBestSellerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = '__all__'


# 중고거래 페이지용
class BookTradeSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    class Meta:
        model = Book
        fields = ('id', 'cover', 'title', 'customer_review_rank', 'adult', 'price_standard', 'category')


# 중고거래 도서 검색 API용
class BookAutocompleteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ['id', 'title']
        

    
class BookAIInputSerializer(serializers.ModelSerializer):
    category = serializers.IntegerField(source="category.id", read_only=True)
    class Meta:
        model = Book
        fields = [
            "id",
            "title",
            "category",
            "author",
            "publisher",
            "description",
            # "sales_point",
            # "best_rank",
            # "customer_review_rank",
            "pub_date",
        ]
          
    
