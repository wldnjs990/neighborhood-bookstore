# books/services/recommand.py
"""
books/recommand.py

추천 페이지에서 사용되는
'추천 후보 도서 50권' 생성 로직

정책 요약:
- 카테고리 필터 (추천 페이지 입력)
- 성인 도서 접근 정책
- sales_point 기반 인기 축
- best_rank / customer_review_rank 조건부 보정
- 출판일 NULL / 미래값은 최후순위
"""

from datetime import date

from django.db.models import (
    F,
    Value,
    FloatField,
    IntegerField,
    Case,
    When,
    ExpressionWrapper,
)
from django.db.models.functions import (
    Log,
)
from django.utils.timezone import now

from books.models import Book


class BookRecommendationCandidate:
    """
    추천 페이지 요청 기준으로
    추천 후보 도서 50권을 선정하는 클래스
    """

    def __init__(self, user, category_ids):
        """
        :param user: request.user
        :param category_ids: 추천 페이지에서 선택한 카테고리 ID 리스트
        """
        self.user = user
        self.category_ids = category_ids

    # ─────────────────────────────
    # 성인 도서 접근 정책
    # ─────────────────────────────
    def _is_adult_allowed(self) -> bool:
        if not self.user.is_authenticated:
            return False

        age = getattr(self.user, "age", None)
        if not age or age < 20:
            return False

        return True

    # ─────────────────────────────
    # 기본 QuerySet (하드 필터)
    # ─────────────────────────────
    def _base_queryset(self):
        qs = Book.objects.all()

        # 카테고리 선택했을 때만 필터
        if self.category_ids:
            qs = qs.filter(category_id__in=self.category_ids)

        # 추천/AI 품질 확보
        qs = qs.exclude(description__isnull=True).exclude(description="")

        # 성인 도서 정책
        if not self._is_adult_allowed():
            qs = qs.filter(adult=False)

        return qs

    # ─────────────────────────────
    # 추천 후보 50권 생성
    # ─────────────────────────────
    def get_top_50(self):
        current_year = now().year

        qs = self._base_queryset().annotate(
            # ── 2️⃣ 판매 지수 (로그 스케일)
            # popularity_score=ExpressionWrapper(
            #     Log(100,F("sales_point") + 1),
            #     output_field=FloatField()
            # ),
            popularity_score=ExpressionWrapper(
                Log(100000, F("sales_point") + 1),
                output_field=FloatField()
            ),
            # ── 3️⃣ 베스트셀러 조건부 보정
            trend_boost=Case(
                When(best_rank__lte=10, then=Value(1.50)),
                When(best_rank__lte=50, then=Value(1.3)),
                When(best_rank__lte=100, then=Value(1.1)),
                default=Value(1.00),
                output_field=FloatField(),
            ),

            # ── 4️⃣ 리뷰 점수 조건부 보정 (숨은 명작)
            review_boost=Case(
                When(customer_review_rank__gte=9, then=Value(1.30)),
                When(customer_review_rank__gte=7, then=Value(1.10)),
                default=Value(1.00),
                output_field=FloatField(),
            ),
        ).annotate(
            # ── 5️⃣ 최종 점수
            final_score=ExpressionWrapper(
                F("popularity_score")
                * F("trend_boost")
                * F("review_boost"),
                output_field=FloatField(),
            )
        )

        return (
            qs.order_by(
                "-final_score",     # ⭐ 최종 추천 점수
            )[:70]
        )
