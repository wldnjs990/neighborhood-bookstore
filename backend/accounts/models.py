from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """커스텀 사용자 모델"""
    nickname = models.CharField(max_length=50, unique=True, null=True, blank=True, verbose_name='닉네임')
    age = models.PositiveIntegerField(null=True, blank=True, verbose_name='나이')
    book_mbti = models.ForeignKey(
        "BookMBTI",
        on_delete=models.SET_NULL,   # MBTI 삭제 시 유저는 유지
        null=True,
        blank=True,
        related_name="users",
        verbose_name="책 MBTI",
    )

    def __str__(self):
        return self.username

class BookMBTI(models.Model):
    """
    도서 MBTI 정의 테이블
    (16가지 고정값)
    - S / F
        F (Fact) 정보형 지식, 교양, 현실 기반 (에세이, 인문, 자기계발, 논픽션) 
        S (Story) 이야기형 스토리, 몰입, 감정 (소설, 판타지, 로맨스)
    - R / I
        R (Realistic) 현실형 현실 배경, 실제 문제 
        I (Imaginary) 상상형 판타지, SF, 세계관 중심
    - E / D
        E (Easy) 쉬움 가볍게 읽힘, 술술 
        D (Deep) 깊음 문장 무거움, 사유 필요
    - P / C
        P (Pace) 전개 빠름 짧은 챕터, 속도감 
        C (Chunk) 전개 느림 분량 많고 묵직
    """
    code = models.CharField(
        max_length=4,
        unique=True,
        verbose_name="MBTI 코드"
    )
    info = models.TextField(
        verbose_name="MBTI 설명 / AI 프롬프트용"
    )
    class Meta:
        db_table = "book_mbti"
        verbose_name = "도서 MBTI"
        verbose_name_plural = "도서 MBTI 목록"

    def __str__(self):
        return self.code