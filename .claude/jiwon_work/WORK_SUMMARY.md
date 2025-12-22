# 도서 데이터 로딩 시스템 구축 작업 요약

## 📋 목차
1. [프로젝트 개요](#프로젝트-개요)
2. [모델 설계](#모델-설계)
3. [데이터 구조](#데이터-구조)
4. [Management Commands](#management-commands)
5. [데이터 로딩 프로세스](#데이터-로딩-프로세스)
6. [주요 이슈 및 해결](#주요-이슈-및-해결)
7. [최종 결과](#최종-결과)

---

## 🎯 프로젝트 개요

### 목적
- 알라딘 도서 API 데이터를 Django 프로젝트에 로드
- 66개의 1Depth 카테고리를 8개 대분류로 재구성
- 약 5,000권의 도서 데이터 정제 및 DB 저장

### 기술 스택
- **Backend**: Django 5.x
- **Database**: SQLite (개발 환경)
- **Data Processing**: pandas, openpyxl, xlrd
- **Environment**: python-decouple

---

## 📊 모델 설계

### 1. Category 모델
```python
class Category(models.Model):
    """도서 카테고리 (8개 대분류)"""
    name = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
```

**8개 대분류**:
1. 소설/시/희곡
2. 경제경영
3. 자기계발
4. 인문/교양
5. 취미/실용
6. 어린이/청소년
7. 학습지
8. 과학

### 2. Book 모델
```python
class Book(models.Model):
    """도서"""
    # 기본 정보
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    isbn = models.CharField(max_length=13, unique=True)
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=200)
    publisher = models.CharField(max_length=100)
    pub_date = models.DateField(null=True, blank=True)

    # 상세 정보
    cover = models.URLField(max_length=500, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    price_standard = models.IntegerField(default=0)
    price_sales = models.IntegerField(default=0)
    adult = models.BooleanField(default=False)

    # 알라딘 정보
    item_id = models.IntegerField(null=True, blank=True)
    mall_type = models.CharField(max_length=20, null=True, blank=True)

    # 알라딘 순위 정보
    customer_review_rank = models.IntegerField(null=True, blank=True)
    best_rank = models.IntegerField(null=True, blank=True)

    # 우리 서비스 평점 (Signal로 자동 업데이트)
    rating_count = models.IntegerField(default=0)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)

    # 타임스탬프
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

**주요 인덱스**:
- `category`: 카테고리별 조회 최적화
- `isbn`: 고유값 제약 조건
- `-average_rating`: 평점순 정렬
- `-created_at`: 최신순 정렬
- `-best_rank`: 베스트셀러 순위
- `-customer_review_rank`: 고객 리뷰 랭킹

---

## 🗂️ 데이터 구조

### 파일 구조
```
backend/
├── books/
│   ├── models.py                    # Book, Category 모델
│   ├── constants.py                 # CATEGORY_MAPPING 상수
│   └── management/commands/
│       ├── load_aladin.py          # 알라딘 엑셀 → categories.json
│       ├── init_extracted_books.py # book_raw.json → extracted_books_fixtures.json
│       └── load_aladin_books.py    # (미완성) 알라딘 API 호출용
├── data/
│   ├── aladin_Category_CID_20210927.xls  # 알라딘 카테고리 원본 (66개)
│   ├── categories.json                    # 8개 대분류 + CID 매핑
│   ├── category_fixtures.json             # Category 테이블 fixture
│   ├── book_raw.json                      # 알라딘 API 원본 데이터
│   └── extracted_books_fixtures.json      # Book 테이블 fixture
└── .gitignore                             # 데이터 파일 제외 설정
```

### categories.json 구조
```json
[
    {
        "pk": 1,
        "name": "소설/시/희곡",
        "cid": [2105, 2330, 4527, ...]  // 해당 대분류에 속한 CID 목록
    },
    ...
]
```

### extracted_books_fixtures.json 구조
```json
[
    {
        "model": "books.book",
        "pk": 1,
        "fields": {
            "category_id": 1,
            "isbn": "9788936438982",
            "title": "할매",
            "author": "황석영",
            "publisher": "창비",
            "pub_date": "2025-12-12",
            "cover": "https://image.aladin.co.kr/...",
            "description": "...",
            "price_standard": 16800,
            "price_sales": 15120,
            "adult": false,
            "item_id": 379665189,
            "mall_type": "BOOK",
            "customer_review_rank": 9,
            "best_rank": 1,
            "created_at": "2025-12-21T20:36:07+09:00",
            "updated_at": "2025-12-21T20:36:07+09:00"
        }
    },
    ...
]
```

---

## ⚙️ Management Commands

### 1. load_aladin
**목적**: 알라딘 엑셀 파일에서 66개 카테고리를 8개 대분류로 그룹핑

**실행**:
```bash
python manage.py load_aladin
```

**처리 과정**:
1. `aladin_Category_CID_20210927.xls` 읽기 (pandas)
2. 1Depth 카테고리별로 CID 그룹핑 (66개)
3. `CATEGORY_MAPPING` 기준으로 8개 대분류로 재그룹핑
4. `categories.json` 생성

**출력**: `data/categories.json`

---

### 2. init_extracted_books
**목적**: 원본 도서 데이터를 정제하여 Django fixture 형식으로 변환

**실행**:
```bash
python manage.py init_extracted_books
```

**처리 과정**:
1. `book_raw.json` 읽기 (알라딘 API 원본 데이터)
2. `categories.json` 읽기 (8개 대분류)
3. 각 도서의 `categoryId`를 CID와 매칭하여 대분류 분류
4. 필드 매핑:
   - `isbn13` → `isbn`
   - `priceStandard` → `price_standard`
   - `pubDate` → `pub_date`
   - etc.
5. **데이터 전처리**:
   - HTML 엔티티 디코딩 (`&lt;` → `<`)
   - HTML 태그 제거
   - 저자명 괄호 제거 (예: `"홍길동 (지은이)"` → `"홍길동"`)
   - 공백 정리
6. 타임존 적용된 `created_at`, `updated_at` 추가
7. `extracted_books_fixtures.json` 생성

**출력**: `data/extracted_books_fixtures.json`

---

### 3. load_aladin_books (미완성)
**목적**: 알라딘 API를 호출하여 실시간 도서 데이터 수집

**계획**:
- 카테고리별 베스트셀러 + 신간 조합
- 국내도서 + 외국도서
- API 호출 제한 고려 (sleep 추가)

---

## 🔄 데이터 로딩 프로세스

### 전체 흐름
```
1. load_aladin 실행
   └─> categories.json 생성

2. (외부) 알라딘 API 호출하여 book_raw.json 생성

3. init_extracted_books 실행
   └─> extracted_books_fixtures.json 생성

4. Category fixture 생성 (Python 스크립트)
   └─> category_fixtures.json 생성

5. loaddata 실행
   ├─> python manage.py loaddata ./data/category_fixtures.json
   └─> python manage.py loaddata ./data/extracted_books_fixtures.json
```

### 실행 명령어
```bash
# 1. 카테고리 JSON 생성
python manage.py load_aladin

# 2. 도서 fixture 생성
python manage.py init_extracted_books

# 3. Category fixture 생성 (Python 스크립트)
python -c "
import json
from datetime import datetime

with open('data/categories.json', 'r', encoding='utf-8') as f:
    categories = json.load(f)

current_time = datetime.now().isoformat()
fixtures = []
for category in categories:
    fixture = {
        'model': 'books.category',
        'pk': category['pk'],
        'fields': {
            'name': category['name'],
            'created_at': current_time
        }
    }
    fixtures.append(fixture)

with open('data/category_fixtures.json', 'w', encoding='utf-8') as f:
    json.dump(fixtures, f, ensure_ascii=False, indent=4)
"

# 4. DB에 로드 (순서 중요!)
python manage.py loaddata ./data/category_fixtures.json
python manage.py loaddata ./data/extracted_books_fixtures.json
```

---

## 🐛 주요 이슈 및 해결

### 1. Excel 파일 형식 문제
**문제**: `.xls` 파일을 읽을 수 없음
```
Missing optional dependency 'xlrd'
```

**원인**: `.xls`는 구형 Excel 형식으로 `xlrd` 패키지 필요

**해결**:
```bash
pip install xlrd
```

**학습**:
- `.xls` (구형) → `xlrd` 사용
- `.xlsx` (신형) → `openpyxl` 사용
- pandas가 확장자 보고 자동으로 적절한 패키지 선택

---

### 2. ISBN 필드 매핑 오류
**문제**: 모든 도서가 동일한 ISBN을 가짐 (5,160개 중 고유값 1개)

**원인**:
```python
# keys_to_copy에 "isbn"이 있는데
keys_to_copy = ["title", "isbn", ...]

# 실제로는 "isbn13"을 체크
elif key == "isbn13":
    fixture_fields["isbn"] = book[key]
```

**해결**:
```python
keys_to_copy = ["title", "isbn13", ...]  # ← "isbn13"으로 수정
```

---

### 3. created_at NOT NULL 에러
**문제**:
```
NOT NULL constraint failed: book.created_at
```

**원인**: Django fixture에 `auto_now_add=True` 필드도 명시해야 함

**해결**:
```python
from django.utils import timezone
current_time = timezone.now().isoformat()
fixture_fields["created_at"] = current_time
fixture_fields["updated_at"] = current_time
```

---

### 4. 외래 키 제약 조건 위반
**문제**:
```
Invalid foreign key: book.category_id contains a value '1'
that does not have a corresponding value in category.id
```

**원인**: Book을 먼저 로드하려 했으나 Category 테이블이 비어있음

**해결**: **Category를 먼저 로드 후 Book 로드**
```bash
# 순서가 중요!
python manage.py loaddata ./data/category_fixtures.json  # 1번
python manage.py loaddata ./data/extracted_books_fixtures.json  # 2번
```

---

### 5. HTML 엔티티 및 태그 문제
**문제**: description 필드에 `&lt;여름은 고작 계절&gt;` 같은 데이터

**원인**: HTML 엔티티 코드가 인코딩된 상태

**해결**:
```python
import html
import re

def clean_description(description):
    if not description:
        return ""

    # 1. HTML 엔티티 디코딩 (&lt; → <, &gt; → >)
    text = html.unescape(description)

    # 2. HTML 태그 제거
    text = re.sub(r'<[^>]+>', '', text)

    # 3. 연속 공백 정리
    text = re.sub(r'\s+', ' ', text)

    # 4. 앞뒤 공백 제거
    return text.strip()
```

**적용**: `title`, `author`, `description` 필드에 모두 적용

---

### 6. RuntimeWarning (타임존)
**문제**:
```
RuntimeWarning: DateTimeField received a naive datetime
while time zone support is active.
```

**원인**: `datetime.now()`는 타임존 정보가 없는 naive datetime 생성

**해결**:
```python
# Before
from datetime import datetime
current_time = datetime.now().isoformat()

# After
from django.utils import timezone
current_time = timezone.now().isoformat()  # 타임존 포함
```

---

## ✅ 최종 결과

### 데이터베이스 상태
- **Categories**: 8개
- **Books**: 5,160개

### 생성된 파일
```
data/
├── categories.json                    # 8개 대분류 + CID 매핑
├── category_fixtures.json             # Category fixture
└── extracted_books_fixtures.json      # Book fixture (정제 완료)
```

### 데이터 품질
✅ ISBN 중복 제거 완료
✅ HTML 엔티티 디코딩 완료
✅ HTML 태그 제거 완료
✅ 저자명 괄호 정보 제거
✅ 타임존 적용 완료
✅ 외래 키 관계 정상

---

## 📚 학습 내용

### Django Management Command
- `management/commands/` 폴더 구조
- `BaseCommand` 상속
- `handle()` 메서드 구현
- `self.stdout.write()` 출력

### Django Fixture
- `auto_now_add`, `auto_now` 필드도 JSON에 명시 필요
- 외래 키 순서: 부모 테이블 먼저 로드
- 타임존 인식 datetime 사용 (`django.utils.timezone`)

### Python 데이터 처리
- pandas로 Excel 읽기 (`pd.read_excel()`)
- HTML 엔티티 디코딩 (`html.unescape()`)
- 정규식 활용 (태그 제거, 텍스트 추출)

### 환경 변수 관리
- `python-decouple` 패키지
- `.env` 파일 활용
- `.gitignore`에 환경 변수 파일 제외

---

## 🔜 다음 단계

### 1. 알라딘 API 실시간 연동
- `load_aladin_books.py` 완성
- 카테고리별 베스트셀러 + 신간 수집
- API 호출 제한 관리

### 2. 추가 모델 구현
- `BookRating`: 사용자 평점
- `Bookmark`: 북마크
- `Trade`: 중고거래

### 3. API 개발
- Django REST Framework 설정
- Serializers 구현
- ViewSets 구현

### 4. 성능 최적화
- 쿼리 최적화 (`select_related`, `prefetch_related`)
- 페이지네이션
- 캐싱 전략

---

## 📝 참고 자료

### 공식 문서
- [Django Management Commands](https://docs.djangoproject.com/en/5.0/howto/custom-management-commands/)
- [Django Fixtures](https://docs.djangoproject.com/en/5.0/howto/initial-data/)
- [pandas Excel I/O](https://pandas.pydata.org/docs/reference/io.html#excel)

### 패키지
- `pandas`: 데이터 처리
- `xlrd`: `.xls` 파일 읽기
- `openpyxl`: `.xlsx` 파일 읽기
- `python-decouple`: 환경 변수 관리
- `requests`: HTTP 요청 (알라딘 API용)

---

**작성일**: 2025-12-21
**작성자**: Claude Code
**프로젝트**: SSAFY 14기 1학기 프로젝트
