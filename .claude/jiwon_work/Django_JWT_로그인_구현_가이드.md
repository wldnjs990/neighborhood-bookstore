# Django JWT 로그인 구현 가이드

## 목차
1. [JWT란 무엇인가?](#1-jwt란-무엇인가)
2. [프로젝트 개요](#2-프로젝트-개요)
3. [구현 단계](#3-구현-단계)
4. [API 사용법](#4-api-사용법)
5. [트러블슈팅](#5-트러블슈팅)

---

## 1. JWT란 무엇인가?

### JWT (JSON Web Token)의 개념
JWT는 사용자 인증을 위한 토큰 기반 인증 방식입니다.

**기존 세션 방식 vs JWT 방식**

- **세션 방식**: 서버가 사용자 정보를 메모리에 저장
  - 단점: 서버에 부담, 확장성 문제

- **JWT 방식**: 사용자 정보를 암호화된 토큰으로 만들어 클라이언트에 전달
  - 장점: 서버 부담 감소, 확장성 좋음, RESTful API에 적합

### JWT의 구조
```
xxxxx.yyyyy.zzzzz
Header.Payload.Signature
```

- **Header**: 토큰 타입과 암호화 알고리즘 정보
- **Payload**: 사용자 정보 (user_id 등)
- **Signature**: 위변조 방지를 위한 서명

### Access Token vs Refresh Token

- **Access Token**: 실제 API 요청 시 사용 (수명: 1시간)
  - 짧은 수명으로 보안 강화

- **Refresh Token**: Access Token 재발급용 (수명: 7일)
  - 사용자가 자주 로그인하지 않아도 됨

---

## 2. 프로젝트 개요

### 구현한 기능
1. ✅ User 모델에 `age` 필드 추가
2. ✅ JWT 인증 시스템 구축
3. ✅ 회원가입 API (회원가입 시 자동 토큰 발급)
4. ✅ 로그인 API (JWT 토큰 발급)
5. ✅ 토큰 갱신 API

### 프로젝트 구조
```
backend/
├── accounts/
│   ├── models.py          # User 모델 정의
│   ├── serializers.py     # 데이터 직렬화 (새로 생성)
│   ├── views.py          # 회원가입 로직
│   └── urls.py           # API 엔드포인트 (새로 생성)
├── bookmarket/
│   ├── settings.py       # JWT 설정 추가
│   └── urls.py          # 메인 URL 라우팅
└── requirements.txt      # JWT 패키지 추가
```

---

## 3. 구현 단계

### Step 1: User 모델에 age 필드 추가

**파일**: `backend/accounts/models.py`

```python
class User(AbstractUser):
    """커스텀 사용자 모델"""
    nickname = models.CharField(max_length=50, unique=True, verbose_name='닉네임')
    age = models.IntegerField(null=True, blank=True, verbose_name='나이')  # ✨ 추가
    book_mbti = models.CharField(
        max_length=4,
        null=True,
        blank=True,
        verbose_name='책 MBTI',
        help_text='사용자의 독서 성향'
    )
```

**왜 `null=True, blank=True`를 사용했나요?**
- `null=True`: 데이터베이스에 NULL 값 허용
- `blank=True`: Django Form에서 필수 입력 아님
- 나이는 선택적 정보이므로 필수가 아님

---

### Step 2: JWT 패키지 설치

**파일**: `backend/requirements.txt`

```txt
djangorestframework-simplejwt==5.4.0  # JWT 토큰 생성/검증
PyJWT==2.10.1                          # JWT 암호화 라이브러리
```

**설치 명령어**:
```bash
pip install djangorestframework-simplejwt==5.4.0 PyJWT==2.10.1
```

---

### Step 3: Django 설정 (settings.py)

**파일**: `backend/bookmarket/settings.py`

#### 3-1. INSTALLED_APPS에 앱 추가
```python
INSTALLED_APPS = [
    # ... 기존 앱들
    'rest_framework',
    'rest_framework_simplejwt',  # ✨ 추가
]
```

#### 3-2. REST Framework 인증 설정
```python
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
}
```

**설명**: 모든 API가 기본적으로 JWT 인증을 사용하도록 설정

#### 3-3. JWT 토큰 수명 설정
```python
from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),      # Access 토큰: 1시간
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),      # Refresh 토큰: 7일
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': False,
    'AUTH_HEADER_TYPES': ('Bearer',),                 # 헤더 형식: Bearer <token>
}
```

**토큰 수명을 다르게 설정한 이유**:
- Access Token은 짧게 → 보안 강화
- Refresh Token은 길게 → 사용자 편의성

---

### Step 4: Serializer 작성

**파일**: `backend/accounts/serializers.py` (새로 생성)

#### 4-1. 회원가입 Serializer

```python
class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'password', 'password_confirm', 'email', 'nickname', 'age')

    def validate(self, data):
        # 비밀번호 확인 검증
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError("비밀번호가 일치하지 않습니다.")
        return data

    def create(self, validated_data):
        # password_confirm은 저장하지 않음
        validated_data.pop('password_confirm')

        # create_user()로 비밀번호 암호화
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password'],
            nickname=validated_data['nickname'],
            age=validated_data.get('age')
        )
        return user
```

**핵심 포인트**:
1. `write_only=True`: 비밀번호는 쓰기만 가능 (응답에 포함 안 됨)
2. `validate()`: 비밀번호 일치 여부 검증
3. `create_user()`: Django의 내장 메서드로 비밀번호를 자동 암호화

#### 4-2. 사용자 정보 Serializer

```python
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'nickname', 'age', 'book_mbti')
        read_only_fields = ('id',)
```

**설명**: 사용자 정보를 JSON 형태로 변환 (응답용)

---

### Step 5: View 작성

**파일**: `backend/accounts/views.py`

```python
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import SignupSerializer, UserSerializer


@api_view(['POST'])
@permission_classes([AllowAny])  # 인증 없이 접근 가능
def signup(request):
    serializer = SignupSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()  # 사용자 생성

        # JWT 토큰 생성
        refresh = RefreshToken.for_user(user)

        return Response({
            'user': UserSerializer(user).data,
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        }, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
```

**흐름 설명**:
1. 클라이언트가 회원가입 데이터 전송
2. `SignupSerializer`로 데이터 검증
3. 검증 성공 → 사용자 생성
4. JWT 토큰 자동 생성 및 반환

**왜 `@permission_classes([AllowAny])`를 사용했나요?**
- 회원가입은 로그인하지 않은 사용자도 접근해야 하므로

---

### Step 6: URL 설정

#### 6-1. accounts 앱 URL

**파일**: `backend/accounts/urls.py` (새로 생성)

```python
from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,    # 로그인
    TokenRefreshView,       # 토큰 갱신
)
from . import views

app_name = 'accounts'

urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
```

**설명**:
- `signup/`: 우리가 만든 커스텀 회원가입
- `login/`: simplejwt가 제공하는 로그인 (username + password → 토큰)
- `token/refresh/`: Refresh Token으로 Access Token 재발급

#### 6-2. 메인 URL 설정

**파일**: `backend/bookmarket/urls.py`

```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/accounts/', include('accounts.urls')),  # ✨ 추가
]
```

---

### Step 7: 마이그레이션

```bash
# 마이그레이션 파일 생성
python manage.py makemigrations

# 데이터베이스에 적용
python manage.py migrate
```

**결과**: User 테이블에 `age` 컬럼이 추가됨

---

## 4. API 사용법

### 4-1. 회원가입

**요청**:
```http
POST http://localhost:8000/api/accounts/signup/
Content-Type: application/json

{
  "username": "jiwon123",
  "password": "securepass123",
  "password_confirm": "securepass123",
  "email": "jiwon@example.com",
  "nickname": "지원",
  "age": 25
}
```

**응답**:
```json
{
  "user": {
    "id": 1,
    "username": "jiwon123",
    "email": "jiwon@example.com",
    "nickname": "지원",
    "age": 25,
    "book_mbti": null
  },
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

---

### 4-2. 로그인

**요청**:
```http
POST http://localhost:8000/api/accounts/login/
Content-Type: application/json

{
  "username": "jiwon123",
  "password": "securepass123"
}
```

**응답**:
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

---

### 4-3. 인증이 필요한 API 호출

**요청 헤더에 Access Token 포함**:
```http
GET http://localhost:8000/api/some-protected-endpoint/
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

**설명**: `Bearer <access_token>` 형식으로 헤더에 포함

---

### 4-4. Access Token 갱신

**요청**:
```http
POST http://localhost:8000/api/accounts/token/refresh/
Content-Type: application/json

{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**응답**:
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."  // 새로운 Access Token
}
```

**언제 사용하나요?**
- Access Token이 만료되었을 때 (1시간 후)
- Refresh Token으로 새 Access Token 발급

---

## 5. 트러블슈팅

### 문제 1: "Authentication credentials were not provided"

**원인**: Authorization 헤더를 포함하지 않음

**해결**:
```http
Authorization: Bearer <your_access_token>
```

---

### 문제 2: "Token is invalid or expired"

**원인**: Access Token이 만료됨 (1시간 경과)

**해결**: Token Refresh API로 새 Access Token 발급

---

### 문제 3: 회원가입 시 "A user with that username already exists"

**원인**: 이미 존재하는 username

**해결**: 다른 username 사용

---

### 문제 4: 비밀번호가 평문으로 저장됨

**원인**: `User.objects.create()` 사용

**해결**: `User.objects.create_user()` 사용 (자동 암호화)

---

## 핵심 정리

### 구현한 파일
| 파일 | 역할 |
|------|------|
| `accounts/models.py` | User 모델에 age 필드 추가 |
| `accounts/serializers.py` | 회원가입/사용자 정보 직렬화 |
| `accounts/views.py` | 회원가입 로직 (토큰 자동 발급) |
| `accounts/urls.py` | 회원가입/로그인/토큰갱신 URL |
| `bookmarket/settings.py` | JWT 인증 설정 |
| `bookmarket/urls.py` | accounts URL 연결 |
| `requirements.txt` | JWT 패키지 추가 |

### API 엔드포인트
| URL | 메서드 | 기능 |
|-----|--------|------|
| `/api/accounts/signup/` | POST | 회원가입 + 토큰 발급 |
| `/api/accounts/login/` | POST | 로그인 + 토큰 발급 |
| `/api/accounts/token/refresh/` | POST | Access Token 갱신 |

### 토큰 사용 흐름
```
1. 회원가입/로그인 → Access Token + Refresh Token 받음
2. API 요청 시 → Authorization: Bearer <access_token>
3. Access Token 만료 (1시간) → Refresh Token으로 재발급
4. Refresh Token도 만료 (7일) → 다시 로그인
```

---

## 다음 단계 (추가 구현 제안)

1. **비밀번호 재설정**: 이메일 인증 기능
2. **사용자 프로필 수정**: PATCH API
3. **로그아웃**: Refresh Token Blacklist 기능
4. **소셜 로그인**: Google, Kakao OAuth 연동
5. **이메일 인증**: 회원가입 시 이메일 인증 단계 추가

---

## 참고 자료

- [Django REST Framework 공식 문서](https://www.django-rest-framework.org/)
- [Simple JWT 공식 문서](https://django-rest-framework-simplejwt.readthedocs.io/)
- [JWT 공식 사이트](https://jwt.io/)
