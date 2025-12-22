from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """커스텀 사용자 모델"""
    nickname = models.CharField(max_length=50, unique=True, null=True, blank=True, verbose_name='닉네임')
    age = models.IntegerField(null=True, blank=True, verbose_name='나이')
    book_mbti = models.CharField(
        max_length=4,
        null=True,
        blank=True,
        verbose_name='책 MBTI',
        help_text='사용자의 독서 성향'
    )

    class Meta:
        db_table = 'user'
        verbose_name = '사용자'
        verbose_name_plural = '사용자'

    def __str__(self):
        return self.username
