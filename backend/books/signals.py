"""
Book 평점 자동 업데이트 Signal
BookRating이 생성/수정/삭제될 때 Book의 average_rating, rating_count 자동 업데이트
"""
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models import Avg, Count
from .models import BookRating


@receiver(post_save, sender=BookRating)
def update_book_rating_on_save(sender, instance, **kwargs):
    """평점 생성/수정 시 Book 평점 필드 자동 업데이트"""
    book = instance.book

    # BookRating 테이블에서 집계
    stats = BookRating.objects.filter(book=book).aggregate(
        avg_rating=Avg('score'),
        count_rating=Count('id')
    )

    # Book 테이블 업데이트
    book.average_rating = stats['avg_rating'] or 0.00
    book.rating_count = stats['count_rating']
    book.save(update_fields=['average_rating', 'rating_count'])


@receiver(post_delete, sender=BookRating)
def update_book_rating_on_delete(sender, instance, **kwargs):
    """평점 삭제 시 Book 평점 필드 자동 업데이트"""
    book = instance.book

    # BookRating 테이블에서 집계
    stats = BookRating.objects.filter(book=book).aggregate(
        avg_rating=Avg('score'),
        count_rating=Count('id')
    )

    # Book 테이블 업데이트
    book.average_rating = stats['avg_rating'] or 0.00
    book.rating_count = stats['count_rating']
    book.save(update_fields=['average_rating', 'rating_count'])
