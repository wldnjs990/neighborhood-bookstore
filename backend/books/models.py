from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator


class Category(models.Model):
    """도서 카테고리"""
    name = models.CharField(max_length=50, unique=True, verbose_name='카테고리명')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일')

    class Meta:
        db_table = 'category'
        verbose_name = '카테고리'
        verbose_name_plural = '카테고리'

    def __str__(self):
        return self.name


class Book(models.Model):
    """도서"""
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='books',
        verbose_name='카테고리'
    )
    isbn = models.CharField(max_length=13, unique=True, verbose_name='ISBN-13')
    title = models.CharField(max_length=200, verbose_name='도서명')
    author = models.CharField(max_length=200, verbose_name='저자')
    publisher = models.CharField(max_length=100, verbose_name='출판사')
    pub_date = models.DateField(null=True, blank=True, verbose_name='출판일')
    cover = models.URLField(max_length=500, null=True, blank=True, verbose_name='표지 이미지 URL')
    description = models.TextField(null=True, blank=True, verbose_name='도서 소개')
    price_standard = models.IntegerField(default=0, verbose_name='정가')
    price_sales = models.IntegerField(default=0, verbose_name='판매가')
    adult = models.BooleanField(default=False, verbose_name='성인 도서 여부')
    item_id = models.IntegerField(
        null=True,
        blank=True,
        verbose_name='알라딘 상품 ID',
        help_text='알라딘 API 상품 ID'
    )
    mall_type = models.CharField(max_length=20, null=True, blank=True, verbose_name='판매처')

    # 알라딘 순위 정보
    customer_review_rank = models.IntegerField(
        null=True,
        blank=True,
        verbose_name='알라딘 고객 리뷰 랭킹',
        help_text='알라딘 고객 리뷰 랭킹 (0~10)'
    )
    best_rank = models.IntegerField(
        null=True,
        blank=True,
        verbose_name='알라딘 베스트셀러 순위',
        help_text='알라딘 베스트셀러 순위'
    )
    sales_point = models.IntegerField(
        null=True,
        blank=True,
        verbose_name='알라딘 판매지수',
        help_text='알라딘 판매지수 (높을수록 많이 팔림)'
    )

    # 우리 서비스 평점 (Signal로 자동 업데이트)
    rating_count = models.IntegerField(
        default=0,
        verbose_name='평점 개수',
        help_text='BookRating 테이블에서 자동 계산'
    )
    average_rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=0.00,
        verbose_name='평균 평점',
        help_text='BookRating 테이블에서 자동 계산 (0.00~5.00)'
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일')

    class Meta:
        db_table = 'book'
        verbose_name = '도서'
        verbose_name_plural = '도서'
        indexes = [
            models.Index(fields=['category'], name='idx_book_category'),
            models.Index(fields=['isbn'], name='idx_book_isbn'),
            models.Index(fields=['-average_rating'], name='idx_book_rating'),
            models.Index(fields=['-created_at'], name='idx_book_created'),
            models.Index(fields=['-best_rank'], name='idx_book_best_rank'),
            models.Index(fields=['-customer_review_rank'], name='idx_book_review_rank'),
            models.Index(fields=['-sales_point'], name='idx_book_sales_point'),
        ]

    def __str__(self):
        return self.title


class BookRating(models.Model):
    """도서 평점 (식별관계 - 복합 PK)"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='ratings',
        verbose_name='사용자'
    )
    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name='ratings',
        verbose_name='도서'
    )
    score = models.DecimalField(
        max_digits=2,
        decimal_places=1,
        validators=[MinValueValidator(0.0), MaxValueValidator(5.0)],
        verbose_name='평점',
        help_text='0.0 ~ 5.0'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일')

    class Meta:
        db_table = 'book_rating'
        verbose_name = '도서 평점'
        verbose_name_plural = '도서 평점'
        constraints = [
            # 식별관계 부여
            models.UniqueConstraint(
                fields=['user', 'book'],
                name='unique_user_book_rating'
            )
        ]
        indexes = [
            models.Index(fields=['book'], name='idx_book_rating_book'),
            models.Index(fields=['-score'], name='idx_book_rating_score'),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.book.title}: {self.score}"


class Bookmark(models.Model):
    """북마크 (식별관계 - 복합 PK)"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='bookmarks',
        verbose_name='사용자'
    )
    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name='bookmarks',
        verbose_name='도서'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일')

    class Meta:
        db_table = 'bookmark'
        verbose_name = '북마크'
        verbose_name_plural = '북마크'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'book'],
                name='unique_user_book_bookmark'
            )
        ]
        indexes = [
            models.Index(fields=['book'], name='idx_bookmark_book'),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.book.title}"
