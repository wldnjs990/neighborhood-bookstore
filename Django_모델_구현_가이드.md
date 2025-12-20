# Django 모델 구현 완료 가이드

## 📋 목차
1. [프로젝트 개요](#프로젝트-개요)
2. [완료된 작업 목록](#완료된-작업-목록)
3. [앱 구조 설명](#앱-구조-설명)
4. [모델 상세 설명](#모델-상세-설명)
5. [Signal 시스템 이해하기](#signal-시스템-이해하기)
6. [마이그레이션 이해하기](#마이그레이션-이해하기)
7. [다음 단계](#다음-단계)

---

## 프로젝트 개요

**프로젝트명**: BookMarket (도서 추천 및 중고거래 플랫폼)

**목적**:
- 사용자가 도서를 탐색하고 평가할 수 있는 시스템
- 사용자 간 중고 도서 거래 기능 제공
- 알라딘 API를 활용한 도서 정보 수집

---

## 완료된 작업 목록

### ✅ 1. accounts 앱 - 사용자 관리
- [x] User 모델 생성 (Django AbstractUser 확장)
- [x] 닉네임, 책 MBTI 필드 추가

### ✅ 2. books 앱 - 도서 관리
- [x] Category 모델 (도서 카테고리)
- [x] Book 모델 (도서 정보)
- [x] BookRating 모델 (도서 평점) - 식별관계, 복합 PK
- [x] Bookmark 모델 (북마크) - 식별관계, 복합 PK
- [x] Signal 추가 (평점 자동 업데이트)

### ✅ 3. trades 앱 - 중고거래
- [x] Trade 모델 (중고거래 게시글)

### ✅ 4. 설정 및 마이그레이션
- [x] settings.py에 앱 등록
- [x] AUTH_USER_MODEL 설정
- [x] 언어/시간대 한국으로 설정
- [x] MEDIA 파일 설정
- [x] Pillow 설치 (이미지 처리)
- [x] 마이그레이션 생성 및 적용

---

## 앱 구조 설명

### Django 앱이란?

Django 앱은 **특정 기능을 담당하는 독립적인 모듈**입니다.

```
프로젝트 = 전체 웹사이트
앱 = 특정 기능 (예: 사용자 관리, 도서 관리, 중고거래)
```

### 왜 앱을 나눴을까요?

#### 나쁜 예 (모든 모델을 한 앱에):
```python
# 하나의 앱에 모든 것
myapp/
  models.py  # User, Book, Category, BookRating, Bookmark, Trade 모두 여기
  views.py   # 모든 뷰가 여기
  # → 파일이 수천 줄, 유지보수 지옥
```

#### 좋은 예 (기능별로 분리):
```python
accounts/    # 사용자 관련
  models.py  # User만
  views.py   # 로그인, 회원가입 등

books/       # 도서 관련
  models.py  # Book, Category, BookRating, Bookmark
  views.py   # 도서 조회, 평점 등

trades/      # 중고거래 관련
  models.py  # Trade
  views.py   # 거래글 CRUD
```

**장점**:
1. ✅ **관심사의 분리**: 각 앱이 하나의 기능만 담당
2. ✅ **유지보수**: 버그 수정 시 해당 앱만 확인
3. ✅ **재사용성**: books 앱을 다른 프로젝트에 복사 가능
4. ✅ **협업**: 팀원 A는 books, 팀원 B는 trades 개발 가능

### 우리 프로젝트 구조

```
backend/
├── bookmarket/          # 프로젝트 설정 (메인 폴더)
│   ├── settings.py      # 전체 설정
│   ├── urls.py          # 전체 URL 라우팅
│   └── wsgi.py
│
├── accounts/            # 사용자 관리 앱
│   ├── models.py        → User
│   ├── views.py         → 로그인, 회원가입 등 (나중에)
│   └── migrations/      → DB 변경 이력
│
├── books/               # 도서 관리 앱
│   ├── models.py        → Book, Category, BookRating, Bookmark
│   ├── signals.py       → 평점 자동 업데이트
│   ├── apps.py          → Signal 등록
│   ├── views.py         → API 뷰 (나중에)
│   └── migrations/      → DB 변경 이력
│
└── trades/              # 중고거래 앱
    ├── models.py        → Trade
    ├── views.py         → 거래글 CRUD (나중에)
    └── migrations/      → DB 변경 이력
```

---

## 모델 상세 설명

### 1. User 모델 (accounts/models.py)

```python
class User(AbstractUser):
    """커스텀 사용자 모델"""
    nickname = models.CharField(max_length=50, unique=True, verbose_name='닉네임')
    book_mbti = models.CharField(
        max_length=4,
        null=True,
        blank=True,
        verbose_name='책 MBTI',
        help_text='사용자의 독서 성향'
    )
```

#### 왜 AbstractUser를 상속했나요?

Django는 기본적으로 User 모델을 제공하지만, 프로젝트마다 필요한 필드가 다릅니다.

**AbstractUser를 상속하면**:
- Django 기본 필드 (username, email, password 등) 모두 사용 가능
- 추가 필드 (nickname, book_mbti) 자유롭게 추가 가능

```python
# Django 기본 User가 제공하는 필드 (자동으로 포함됨):
# - username (로그인 ID)
# - email
# - password (암호화되어 저장)
# - first_name, last_name
# - is_staff (관리자 여부)
# - is_active (활성화 여부)
# - date_joined (가입일)

# 우리가 추가한 필드:
# - nickname (닉네임)
# - book_mbti (독서 성향)
```

#### 필드 옵션 설명

```python
max_length=50         # 최대 50자까지 입력 가능
unique=True           # 중복 불가 (DB에서 자동 체크)
null=True             # DB에 NULL 저장 가능
blank=True            # Django Form에서 빈 값 허용
verbose_name='닉네임' # Admin 페이지에서 보이는 이름
help_text='설명'      # Admin 페이지에서 보이는 도움말
```

**null vs blank 차이**:
- `null=True`: **데이터베이스** 레벨 (NULL 저장 가능)
- `blank=True`: **Django Form** 레벨 (빈 값 입력 가능)

```python
# 예시
book_mbti = models.CharField(null=True, blank=True)
# → DB에 NULL 저장 가능 + Form에서 빈 값 입력 가능

book_mbti = models.CharField(null=False, blank=True)
# → DB에 빈 문자열('') 저장 + Form에서 빈 값 입력 가능
# → NULL은 안 됨!
```

#### Meta 클래스란?

```python
class Meta:
    db_table = 'user'                # DB 테이블 이름
    verbose_name = '사용자'          # Admin에서 단수형 이름
    verbose_name_plural = '사용자'   # Admin에서 복수형 이름
```

**Meta 클래스가 없으면**:
- 테이블명: `accounts_user` (앱이름_모델명, 자동 생성)
- Admin 이름: `User`, `Users`

**Meta 클래스를 추가하면**:
- 테이블명: `user` (우리가 지정)
- Admin 이름: `사용자` (한글 이름)

---

### 2. Category 모델 (books/models.py)

```python
class Category(models.Model):
    """도서 카테고리"""
    name = models.CharField(max_length=50, unique=True, verbose_name='카테고리명')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일')
```

**간단한 모델**입니다.

#### auto_now_add vs auto_now

```python
created_at = models.DateTimeField(auto_now_add=True)
# 생성될 때 "한 번만" 현재 시간 저장
# 이후 수정해도 변경 안 됨

updated_at = models.DateTimeField(auto_now=True)
# 생성 + 수정할 때 "매번" 현재 시간으로 업데이트
```

**실제 동작**:
```python
# 카테고리 생성
category = Category.objects.create(name='소설')
# created_at = 2024-01-01 10:00:00 (현재 시간)

# 카테고리 수정
category.name = '문학'
category.save()
# created_at = 2024-01-01 10:00:00 (변경 안 됨!)
```

---

### 3. Book 모델 (books/models.py)

```python
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
    # ... 다른 필드들
```

#### ForeignKey란?

**ForeignKey = 다른 테이블을 참조하는 관계**

```python
# Book → Category 관계
book = Book.objects.create(
    title='해리포터',
    category=category_novel  # Category 객체를 직접 할당
)

# 사용 예시
print(book.category.name)  # '소설'
```

#### on_delete 옵션 (중요!)

**on_delete는 "부모가 삭제될 때 어떻게 할까?"를 정의합니다.**

```python
category = models.ForeignKey(
    Category,
    on_delete=models.SET_NULL,  # ← 이 부분!
    null=True
)
```

**옵션 종류**:

| 옵션 | 의미 | 예시 |
|------|------|------|
| `CASCADE` | 부모 삭제 시 자식도 삭제 | 사용자 삭제 → 평점도 삭제 |
| `SET_NULL` | 부모 삭제 시 FK만 NULL | 카테고리 삭제 → book의 category_id만 NULL |
| `PROTECT` | 자식이 있으면 부모 삭제 불가 | 평점 있는 사용자는 삭제 못함 |
| `SET_DEFAULT` | 부모 삭제 시 기본값으로 | 거의 안 씀 |

**시나리오**:
```python
# 1. CASCADE (자식도 삭제)
user = models.ForeignKey(User, on_delete=models.CASCADE)

user.delete()
# → 이 사용자의 모든 평점도 삭제!

# 2. SET_NULL (FK만 NULL)
category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)

category.delete()
# → 책은 유지, category_id만 NULL로
```

#### related_name이란?

**역참조를 위한 이름**입니다.

```python
category = models.ForeignKey(
    Category,
    related_name='books'  # ← 이 부분!
)
```

**없으면**:
```python
# Category → Book 역참조
category.book_set.all()  # 자동 생성된 이름
```

**있으면**:
```python
# Category → Book 역참조
category.books.all()  # 우리가 지정한 이름 (더 직관적!)
```

**실제 사용 예시**:
```python
# 소설 카테고리 가져오기
novel = Category.objects.get(name='소설')

# 이 카테고리의 모든 책 가져오기 (역참조!)
books = novel.books.all()
# → SELECT * FROM book WHERE category_id = novel.id

for book in books:
    print(book.title)
# 출력: 해리포터, 반지의 제왕, ...
```

#### 인덱스란?

```python
class Meta:
    indexes = [
        models.Index(fields=['category'], name='idx_book_category'),
        models.Index(fields=['-average_rating'], name='idx_book_rating'),
    ]
```

**인덱스 = 검색 속도를 높이는 DB 기능**

**인덱스가 없으면**:
```sql
SELECT * FROM book WHERE category_id = 5;
-- 전체 테이블 스캔 (책 100만 권 모두 확인)
-- 매우 느림!
```

**인덱스가 있으면**:
```sql
SELECT * FROM book WHERE category_id = 5;
-- 인덱스로 바로 찾기
-- 매우 빠름!
```

**`-` 기호의 의미**:
```python
fields=['-average_rating']  # 내림차순 인덱스
# → 평점 높은 순으로 정렬할 때 빠름
```

---

### 4. BookRating 모델 (식별관계, 복합 PK)

```python
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
    # ...

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'book'],
                name='unique_user_book_rating'
            )
        ]
```

#### 왜 복합 PK (UniqueConstraint)를 사용했나요?

**문제**: id를 PK로 사용하면 중복 평점 가능
```python
# id가 PK인 경우
평점1: id=1, user=1, book=1, score=5.0
평점2: id=2, user=1, book=1, score=4.0  # 중복! (같은 사람이 같은 책에 2번 평점)
```

**해결**: (user, book) 복합 유니크 제약
```python
# UniqueConstraint 사용
평점1: user=1, book=1, score=5.0  ✅
평점2: user=1, book=1, score=4.0  ❌ DB 에러! (중복 불가)
평점3: user=1, book=2, score=4.0  ✅ (다른 책이므로 OK)
평점4: user=2, book=1, score=3.0  ✅ (다른 사람이므로 OK)
```

**Django에서 복합 PK 표현 방법**:
```python
# 방법 1: UniqueConstraint (권장!)
constraints = [
    models.UniqueConstraint(
        fields=['user', 'book'],
        name='unique_user_book_rating'
    )
]

# 방법 2: unique_together (옛날 방식, 비권장)
unique_together = [['user', 'book']]
```

#### settings.AUTH_USER_MODEL이란?

```python
user = models.ForeignKey(
    settings.AUTH_USER_MODEL,  # ← 이 부분!
    on_delete=models.CASCADE
)
```

**왜 직접 User를 참조하지 않나요?**

```python
# ❌ 나쁜 예
from accounts.models import User
user = models.ForeignKey(User, ...)

# ✅ 좋은 예
from django.conf import settings
user = models.ForeignKey(settings.AUTH_USER_MODEL, ...)
```

**이유**:
1. **유연성**: 나중에 User 모델이 바뀌어도 코드 수정 불필요
2. **순환 참조 방지**: books 앱이 accounts 앱을 import하지 않아도 됨
3. **Django 권장 방식**

#### DecimalField란?

```python
score = models.DecimalField(
    max_digits=2,      # 전체 자릿수
    decimal_places=1   # 소수점 자릿수
)
```

**값 예시**:
- `max_digits=2, decimal_places=1` → 0.0 ~ 9.9
- `max_digits=3, decimal_places=2` → 0.00 ~ 9.99
- `max_digits=5, decimal_places=2` → 0.00 ~ 999.99

**왜 FloatField가 아닌 DecimalField?**

```python
# FloatField (부동소수점) - 오차 발생!
0.1 + 0.2 = 0.30000000000000004  # ❌ 정확하지 않음!

# DecimalField (고정소수점) - 정확!
0.1 + 0.2 = 0.3  # ✅ 정확함!
```

**평점, 가격 등 정확성이 중요한 경우 DecimalField 사용!**

#### Validator란?

```python
score = models.DecimalField(
    max_digits=2,
    decimal_places=1,
    validators=[MinValueValidator(0.0), MaxValueValidator(5.0)]
)
```

**Validator = 값의 유효성을 검사하는 함수**

```python
# 사용자가 6.0 입력 시
rating = BookRating(user=user, book=book, score=6.0)
rating.save()
# → ValidationError: 5.0 이하여야 합니다!

# 사용자가 -1.0 입력 시
rating = BookRating(user=user, book=book, score=-1.0)
rating.save()
# → ValidationError: 0.0 이상이어야 합니다!
```

---

### 5. Bookmark 모델 (식별관계, 복합 PK)

BookRating과 동일한 패턴입니다.

```python
class Bookmark(models.Model):
    """북마크 (식별관계 - 복합 PK)"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'book'],
                name='unique_user_book_bookmark'
            )
        ]
```

**의미**: 한 사용자가 같은 책을 여러 번 북마크할 수 없음

---

### 6. Trade 모델 (비식별관계)

```python
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

    # ...
    sale_type = models.CharField(
        max_length=10,
        choices=SALE_TYPE_CHOICES,
        default='sale',
        verbose_name='판매 유형'
    )
```

#### choices란?

**choices = 선택 가능한 값들을 미리 정의**

```python
# 사용 예시
trade = Trade.objects.create(
    title='해리포터 팝니다',
    sale_type='sale'  # 'sale' 또는 'free'만 가능
)

# Admin 페이지에서 드롭다운으로 표시
# [ 판매 ▼ ]  또는  [ 무료나눔 ▼ ]
```

**choices가 없으면**:
```python
sale_type = models.CharField(max_length=10)
# → 아무 값이나 입력 가능 (오타 발생 가능)
# → 'sell', 'Sale', 'SALE', 'selling' 등 일관성 없음
```

**choices를 사용하면**:
```python
sale_type = models.CharField(max_length=10, choices=SALE_TYPE_CHOICES)
# → 'sale' 또는 'free'만 가능
# → DB 레벨에서는 검증 안 됨 (Django 레벨에서만)
```

**DB 레벨 검증까지 추가하려면**:
```python
from django.db.models import Q, CheckConstraint

class Meta:
    constraints = [
        CheckConstraint(
            check=Q(sale_type__in=['sale', 'free']),
            name='valid_sale_type'
        )
    ]
```

#### ImageField란?

```python
image = models.ImageField(
    upload_to='trade_images/',
    null=True,
    blank=True
)
```

**ImageField = 이미지 파일을 업로드하고 저장하는 필드**

**실제 저장 위치**:
```python
# settings.py
MEDIA_ROOT = BASE_DIR / 'media'
MEDIA_URL = '/media/'

# 파일 업로드 시
image = models.ImageField(upload_to='trade_images/')
# → 실제 저장: media/trade_images/파일명.jpg
# → URL: http://localhost:8000/media/trade_images/파일명.jpg
```

**Pillow가 필요한 이유**:
- ImageField는 Pillow 라이브러리를 사용
- Pillow = Python 이미지 처리 라이브러리
- 이미지 크기 확인, 리사이징 등 기능 제공

---

## Signal 시스템 이해하기

### Signal이란?

**Signal = 특정 이벤트가 발생했을 때 자동으로 실행되는 함수**

**예시**:
```
평점 생성 → Signal 발동 → Book의 평점 자동 업데이트
```

### 왜 Signal이 필요한가요?

**문제 상황**:
```python
# Book 모델에 평점 필드가 있음
class Book(models.Model):
    average_rating = models.DecimalField(default=0.00)
    rating_count = models.IntegerField(default=0)

# 사용자가 평점을 주면?
rating = BookRating.objects.create(user=user, book=book, score=5.0)

# Book의 평점 필드는 자동으로 업데이트 안 됨!
print(book.average_rating)  # 0.00 (여전히)
print(book.rating_count)    # 0 (여전히)
```

**해결 1: 수동으로 업데이트** (나쁜 방법)
```python
# 평점 생성할 때마다 이렇게 해야 함
rating = BookRating.objects.create(user=user, book=book, score=5.0)

# 평점 재계산
stats = BookRating.objects.filter(book=book).aggregate(
    avg=Avg('score'),
    count=Count('id')
)
book.average_rating = stats['avg']
book.rating_count = stats['count']
book.save()

# → 코드 중복, 실수하기 쉬움, 유지보수 어려움
```

**해결 2: Signal 사용** (좋은 방법)
```python
# Signal이 자동으로 처리!
rating = BookRating.objects.create(user=user, book=book, score=5.0)
# → Signal이 자동 실행 → Book 평점 업데이트 완료!

print(book.average_rating)  # 5.00 (자동 업데이트됨!)
print(book.rating_count)    # 1 (자동 업데이트됨!)
```

### Signal 코드 분석

```python
# books/signals.py
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
```

#### 코드 한 줄씩 이해하기

**1. Signal 임포트**
```python
from django.db.models.signals import post_save, post_delete
```
- `post_save`: 모델이 저장된 **후**에 발생하는 Signal
- `post_delete`: 모델이 삭제된 **후**에 발생하는 Signal

**2. receiver 데코레이터**
```python
@receiver(post_save, sender=BookRating)
def update_book_rating_on_save(sender, instance, **kwargs):
```
- `@receiver`: 이 함수를 Signal 리스너로 등록
- `post_save`: 어떤 Signal을 받을지
- `sender=BookRating`: 어떤 모델의 Signal인지

**의미**: "BookRating이 저장될 때마다 이 함수 실행"

**3. 함수 파라미터**
```python
def update_book_rating_on_save(sender, instance, **kwargs):
```
- `sender`: Signal을 보낸 모델 클래스 (BookRating)
- `instance`: 저장된 객체 (예: BookRating 객체)
- `**kwargs`: 추가 인자들

**4. 집계 쿼리**
```python
stats = BookRating.objects.filter(book=book).aggregate(
    avg_rating=Avg('score'),
    count_rating=Count('id')
)
```

**SQL로 변환하면**:
```sql
SELECT
    AVG(score) AS avg_rating,
    COUNT(id) AS count_rating
FROM book_rating
WHERE book_id = 1;
```

**결과**:
```python
stats = {
    'avg_rating': 4.5,  # 평균 평점
    'count_rating': 10  # 평점 개수
}
```

**5. Book 업데이트**
```python
book.average_rating = stats['avg_rating'] or 0.00
book.rating_count = stats['count_rating']
book.save(update_fields=['average_rating', 'rating_count'])
```

- `stats['avg_rating'] or 0.00`: 평점이 없으면 0.00
- `update_fields`: 특정 필드만 업데이트 (성능 최적화)

### Signal 등록 (중요!)

```python
# books/apps.py
class BooksConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'books'

    def ready(self):
        """앱이 준비될 때 Signal 등록"""
        import books.signals
```

**왜 필요한가요?**

Signal 파일을 만들었지만, Django가 자동으로 읽지 않습니다!

```python
# Signal 등록 안 하면
평점 생성 → Signal 실행 안 됨 → Book 평점 업데이트 안 됨

# Signal 등록하면
평점 생성 → Signal 실행 → Book 평점 자동 업데이트!
```

**ready() 메서드**:
- Django 앱이 시작될 때 한 번 실행
- 여기서 Signal 파일을 import하면 Signal이 등록됨

### Signal 실행 흐름

```
1. 사용자가 평점 등록
   ↓
2. BookRating.objects.create(user=user, book=book, score=5.0)
   ↓
3. Django가 DB에 저장
   ↓
4. post_save Signal 발생
   ↓
5. update_book_rating_on_save() 함수 실행
   ↓
6. BookRating 집계 (AVG, COUNT)
   ↓
7. Book의 average_rating, rating_count 업데이트
   ↓
8. 완료!
```

### Signal 테스트 예시

```python
# Django Shell에서 테스트
python manage.py shell

# 1. 사용자와 책 생성
from accounts.models import User
from books.models import Book, BookRating

user1 = User.objects.create_user(username='user1', password='pass')
user2 = User.objects.create_user(username='user2', password='pass')
book = Book.objects.create(title='해리포터', isbn='1234567890123')

print(f"평점 전: {book.average_rating}, {book.rating_count}")
# 출력: 평점 전: 0.00, 0

# 2. 평점 추가
rating1 = BookRating.objects.create(user=user1, book=book, score=5.0)
book.refresh_from_db()  # DB에서 다시 읽기
print(f"평점 1개: {book.average_rating}, {book.rating_count}")
# 출력: 평점 1개: 5.00, 1

# 3. 평점 추가
rating2 = BookRating.objects.create(user=user2, book=book, score=3.0)
book.refresh_from_db()
print(f"평점 2개: {book.average_rating}, {book.rating_count}")
# 출력: 평점 2개: 4.00, 2 (5.0 + 3.0 = 8.0 / 2 = 4.0)

# 4. 평점 삭제
rating1.delete()
book.refresh_from_db()
print(f"평점 1개: {book.average_rating}, {book.rating_count}")
# 출력: 평점 1개: 3.00, 1

# Signal이 자동으로 평점을 업데이트했습니다!
```

---

## 마이그레이션 이해하기

### 마이그레이션이란?

**마이그레이션 = Django 모델을 실제 DB 테이블로 만드는 작업**

```
Django 모델 (Python 코드)
    ↓ makemigrations
마이그레이션 파일 (SQL 변환 전 단계)
    ↓ migrate
DB 테이블 (실제 테이블 생성)
```

### 왜 필요한가요?

**모델을 작성했지만, DB에는 아직 테이블이 없습니다!**

```python
# models.py에 작성
class Book(models.Model):
    title = models.CharField(max_length=200)
    # ...

# 하지만 DB에는 book 테이블이 없음!
# → makemigrations + migrate 필요
```

### 마이그레이션 명령어

#### 1. makemigrations

```bash
python manage.py makemigrations
```

**하는 일**:
- 모델 변경 사항을 감지
- 마이그레이션 파일 생성 (Python 파일)
- **DB는 아직 변경 안 됨!**

**생성된 파일**:
```
accounts/migrations/0001_initial.py
books/migrations/0001_initial.py
trades/migrations/0001_initial.py
```

**마이그레이션 파일 내용 예시**:
```python
# books/migrations/0001_initial.py
class Migration(migrations.Migration):
    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Book',
            fields=[
                ('id', models.BigAutoField(primary_key=True)),
                ('title', models.CharField(max_length=200)),
                # ...
            ],
        ),
    ]
```

#### 2. migrate

```bash
python manage.py migrate
```

**하는 일**:
- 마이그레이션 파일을 읽음
- 실제 DB에 테이블 생성/수정
- **이제 DB가 변경됨!**

**실행 결과**:
```
Applying accounts.0001_initial... OK
Applying books.0001_initial... OK
Applying trades.0001_initial... OK
```

**실제 실행된 SQL** (확인 방법):
```bash
python manage.py sqlmigrate books 0001
```

```sql
-- 출력 예시
CREATE TABLE "book" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    "category_id" integer NULL REFERENCES "category" ("id"),
    "isbn" varchar(13) NOT NULL UNIQUE,
    "title" varchar(200) NOT NULL,
    -- ...
);
```

### 마이그레이션 흐름

```
1. models.py 작성/수정
   ↓
2. python manage.py makemigrations
   → 마이그레이션 파일 생성
   ↓
3. python manage.py migrate
   → DB 테이블 생성/수정
   ↓
4. 완료!
```

### 마이그레이션 파일 관리

**마이그레이션 파일 = 버전 관리**

```
books/migrations/
├── 0001_initial.py        # 최초 테이블 생성
├── 0002_book_price.py     # price 필드 추가
├── 0003_alter_book_isbn.py # isbn 필드 수정
└── ...
```

**특징**:
- 순서대로 실행됨 (0001 → 0002 → 0003)
- Git에 포함해야 함 (팀원과 공유)
- 삭제하면 안 됨!

### 마이그레이션 주의사항

#### 1. 마이그레이션 전에 백업
```bash
# SQLite 백업
cp db.sqlite3 db.sqlite3.backup
```

#### 2. 마이그레이션 확인
```bash
# 어떤 마이그레이션이 실행되었는지 확인
python manage.py showmigrations

# 결과
accounts
 [X] 0001_initial
books
 [X] 0001_initial
trades
 [X] 0001_initial
```

#### 3. 마이그레이션 되돌리기
```bash
# 특정 마이그레이션으로 되돌리기
python manage.py migrate books 0001

# 모든 마이그레이션 되돌리기
python manage.py migrate books zero
```

---

## 다음 단계

### 1. Admin 등록

모델을 만들었으니 Admin 페이지에서 확인해봅시다!

```python
# books/admin.py
from django.contrib import admin
from .models import Category, Book, BookRating, Bookmark

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'created_at']
    search_fields = ['name']

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'author', 'category', 'average_rating', 'rating_count']
    list_filter = ['category', 'adult']
    search_fields = ['title', 'author', 'isbn']

@admin.register(BookRating)
class BookRatingAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'book', 'score', 'created_at']
    list_filter = ['score']

@admin.register(Bookmark)
class BookmarkAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'book', 'created_at']
```

**superuser 생성**:
```bash
python manage.py createsuperuser
# Username: admin
# Email: admin@example.com
# Password: ****

python manage.py runserver
# http://localhost:8000/admin 접속
```

### 2. Django REST Framework 설정

API를 만들기 위해 DRF를 설치합니다.

```bash
pip install djangorestframework
```

```python
# settings.py
INSTALLED_APPS = [
    # ...
    'rest_framework',
]
```

### 3. Serializer 작성

**Serializer = 모델을 JSON으로 변환**

```python
# books/serializers.py
from rest_framework import serializers
from .models import Book, BookRating

class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = '__all__'

class BookRatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookRating
        fields = '__all__'
```

### 4. View 작성

```python
# books/views.py
from rest_framework import viewsets
from .models import Book, BookRating
from .serializers import BookSerializer, BookRatingSerializer

class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer

class BookRatingViewSet(viewsets.ModelViewSet):
    queryset = BookRating.objects.all()
    serializer_class = BookRatingSerializer
```

### 5. URL 설정

```python
# books/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BookViewSet, BookRatingViewSet

router = DefaultRouter()
router.register('books', BookViewSet)
router.register('ratings', BookRatingViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
```

```python
# bookmarket/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/books/', include('books.urls')),
]
```

### 6. 테스트

```bash
# 서버 실행
python manage.py runserver

# API 테스트
# GET http://localhost:8000/api/books/books/
# POST http://localhost:8000/api/books/ratings/
```

---

## 핵심 개념 정리

### Django 모델 핵심 개념

1. **모델 = 테이블**: 클래스 하나가 테이블 하나
2. **필드 = 컬럼**: 필드 하나가 컬럼 하나
3. **ForeignKey = 관계**: 다른 테이블과의 연결
4. **Meta**: 테이블 이름, 인덱스 등 메타데이터
5. **Signal**: 자동화 (이벤트 기반 처리)
6. **마이그레이션**: 모델 → DB 테이블

### 주요 필드 타입

| 필드 타입 | 용도 | 예시 |
|-----------|------|------|
| CharField | 짧은 문자열 | 제목, 이름 |
| TextField | 긴 문자열 | 내용, 설명 |
| IntegerField | 정수 | 나이, 개수 |
| DecimalField | 정확한 소수 | 가격, 평점 |
| BooleanField | 참/거짓 | 성인 여부 |
| DateTimeField | 날짜+시간 | 생성일, 수정일 |
| ForeignKey | 다른 모델 참조 | 카테고리, 사용자 |
| ImageField | 이미지 파일 | 프로필, 상품 이미지 |

### 주요 옵션

| 옵션 | 의미 |
|------|------|
| max_length | 최대 길이 |
| unique | 중복 불가 |
| null | DB에 NULL 가능 |
| blank | Form에서 빈 값 가능 |
| default | 기본값 |
| choices | 선택 가능한 값 |
| auto_now_add | 생성 시 현재 시간 |
| auto_now | 수정 시 현재 시간 |
| on_delete | 부모 삭제 시 동작 |
| related_name | 역참조 이름 |

---

## 자주 하는 실수

### 1. 마이그레이션 안 하기

```python
# models.py 수정
class Book(models.Model):
    new_field = models.CharField(max_length=100)

# 에러 발생!
# → makemigrations + migrate 잊지 말기!
```

### 2. null과 blank 혼동

```python
# CharField에 null=True (잘못됨)
name = models.CharField(max_length=50, null=True)
# → 빈 문자열('')과 NULL 두 가지 "빈 값" 존재 (혼란)

# CharField에 blank=True (올바름)
name = models.CharField(max_length=50, blank=True, default='')
# → 빈 문자열('')만 사용
```

### 3. ForeignKey on_delete 누락

```python
# 에러 발생!
category = models.ForeignKey(Category)

# 올바름
category = models.ForeignKey(Category, on_delete=models.CASCADE)
```

### 4. Signal 등록 안 하기

```python
# signals.py 만들었지만 apps.py에 등록 안 함
# → Signal 실행 안 됨!

# apps.py에 ready() 메서드 추가 필수!
def ready(self):
    import books.signals
```

---

## 마무리

축하합니다! 🎉

다음 작업을 완료했습니다:

1. ✅ 3개 앱 생성 (accounts, books, trades)
2. ✅ 6개 모델 작성 (User, Category, Book, BookRating, Bookmark, Trade)
3. ✅ Signal 시스템 구현 (평점 자동 업데이트)
4. ✅ 마이그레이션 완료 (DB 테이블 생성)

**이제 할 수 있는 것**:
- Admin 페이지에서 데이터 관리
- Django ORM으로 데이터 조작
- API 개발 (DRF)
- 프론트엔드 연동

**다음 학습 주제**:
1. Django Admin 커스터마이징
2. Django REST Framework (DRF)
3. Serializer 작성
4. ViewSet과 Router
5. 인증/권한 (JWT)
6. 알라딘 API 연동
7. 프론트엔드 연동 (Vue, React 등)

**참고 자료**:
- Django 공식 문서: https://docs.djangoproject.com/
- DRF 공식 문서: https://www.django-rest-framework.org/
- Django 한국 커뮤니티: https://django-korea.readthedocs.io/

화이팅! 🚀
