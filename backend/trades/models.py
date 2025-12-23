from django.db import models
from django.conf import settings
from books.models import Book


class Trade(models.Model):
    """중고거래"""

    SALE_TYPE_CHOICES = [
        ('sale', '판매'),
        ('free', '무료나눔'),
    ]

    STATUS_CHOICES = [
        ('available', '판매중'),
        ('reserved', '예약중'),
        ('sold', '판매완료'),
    ]

    REGION_CHOICES = [
    ('all', '전국'),
    ('seoul', '서울특별시'),
    ('busan', '부산광역시'),
    ('daegu', '대구광역시'),
    ('incheon', '인천광역시'),
    ('gwangju', '광주광역시'),
    ('daejeon', '대전광역시'),
    ('ulsan', '울산광역시'),
    ('sejong', '세종특별자치시'),
    ('gyeonggi', '경기도'),
    ('gangwon', '강원특별자치도'),
    ('chungbuk', '충청북도'),
    ('chungnam', '충청남도'),
    ('jeonbuk', '전라북도'),
    ('jeonnam', '전라남도'),
    ('gyeongbuk', '경상북도'),
    ('gyeongnam', '경상남도'),
    ('jeju', '제주특별자치도'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='trades',
        verbose_name='판매자'
    )
    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name='trades',
        verbose_name='도서'
    )
    title = models.CharField(max_length=200, verbose_name='판매글 제목')
    content = models.TextField(verbose_name='판매글 내용')
    sale_type = models.CharField(
        max_length=10,
        choices=SALE_TYPE_CHOICES,
        default='sale',
        verbose_name='판매 유형'
    )
    price = models.IntegerField(default=0, verbose_name='판매가격')
    region = models.CharField(
        max_length=20,
        choices=REGION_CHOICES,
        verbose_name='거래 지역'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='available',
        verbose_name='거래 상태'
    )
    image = models.ImageField(
        upload_to='trade_images/',
        null=True,
        blank=True,
        verbose_name='상품 이미지'
    )
    kakao_chat_url = models.URLField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name='카카오톡 오픈채팅 URL'
    )
    view_count = models.IntegerField(default=0, verbose_name='조회수')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일')

    class Meta:
        db_table = 'trade'
        verbose_name = '중고거래'
        verbose_name_plural = '중고거래'
        indexes = [
            models.Index(fields=['user'], name='idx_trade_user'),
            models.Index(fields=['book'], name='idx_trade_book'),
            models.Index(fields=['status'], name='idx_trade_status'),
            models.Index(fields=['-created_at'], name='idx_trade_created'),
            models.Index(fields=['region'], name='idx_trade_region'),
        ]

    def __str__(self):
        return f"{self.title} - {self.user.username}"
