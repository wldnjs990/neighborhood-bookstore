# REST_FRAMEWORK 설정 상세 설명

## 1. rest_framework_simplejwt는 무엇인가?

### 패키지 관계도
```
Django (웹 프레임워크)
  │
  └── Django REST Framework (DRF) - API 구축 도구
        │
        ├── rest_framework.authentication.SessionAuthentication (기본 제공)
        ├── rest_framework.authentication.BasicAuthentication (기본 제공)
        │
        └── rest_framework_simplejwt (서드파티 플러그인)
              └── JWTAuthentication (JWT 토큰 인증)
```

### 답변
**네, `rest_framework_simplejwt`는 DRF의 서드파티 플러그인입니다.**

- Django REST Framework 자체는 기본 인증 방식만 제공
- JWT 인증을 위해 `simplejwt` 플러그인 설치 필요
- DRF의 인증 시스템을 확장하는 방식으로 동작

---

## 2. REST_FRAMEWORK는 무엇인가?

### 기본 개념
`REST_FRAMEWORK`는 **Django REST Framework의 전역 설정을 담는 딕셔너리**입니다.

Django의 `settings.py`는 여러 패키지의 설정을 관리:

```python
# Django 기본 설정
DEBUG = True                    # Django 설정
ALLOWED_HOSTS = []             # Django 설정
AUTH_USER_MODEL = 'accounts.User'  # Django 설정

# Django REST Framework 설정
REST_FRAMEWORK = {             # DRF 설정
    'DEFAULT_AUTHENTICATION_CLASSES': [...],
    'DEFAULT_PERMISSION_CLASSES': [...],
}

# Simple JWT 설정
SIMPLE_JWT = {                 # simplejwt 설정
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),
}
```

### 답변
**아니요, Django의 기본 문법이 아닙니다.**
- Django REST Framework 패키지를 위한 설정 딕셔너리
- DRF가 설치되어 있어야 의미가 있음
- DRF가 `settings.py`의 `REST_FRAMEWORK` 변수를 읽어서 동작 방식 결정

---

## 3. REST_FRAMEWORK가 로그인 기능을 연결하는가?

### 정확한 역할
`REST_FRAMEWORK`는 **로그인 기능을 연결하는 것이 아니라**, **인증 방식을 지정**합니다.

### 비유로 이해하기

#### 비유: 출입문 시스템
```
건물 출입구 (API 엔드포인트)
  │
  └── 보안 시스템 (REST_FRAMEWORK 설정)
        │
        ├── 인증 방식 선택:
        │   ① 지문 인식 (SessionAuthentication)
        │   ② 비밀번호 입력 (BasicAuthentication)
        │   ③ 카드키 (JWTAuthentication) ← 우리가 선택한 방식
        │
        └── 인증 성공 → 출입 허가
```

### 실제 코드로 보는 흐름

#### 설정 (settings.py)
```python
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
}
```

**의미**: "모든 API에서 기본적으로 JWT 토큰으로 사용자 인증을 확인하겠다"

---

#### 사용 예시

##### 1. 인증이 필요 없는 API (회원가입, 로그인)
```python
from rest_framework.permissions import AllowAny

@api_view(['POST'])
@permission_classes([AllowAny])  # 인증 건너뛰기
def signup(request):
    # 누구나 접근 가능
    pass
```

##### 2. 인증이 필요한 API (프로필 조회)
```python
@api_view(['GET'])
def my_profile(request):
    # REST_FRAMEWORK 설정 덕분에 자동으로 JWT 인증 수행
    # request.user에 인증된 사용자 정보가 채워짐
    return Response({
        'username': request.user.username,
        'email': request.user.email,
    })
```

---

## 4. 전체 인증 흐름

### Step 1: 로그인 (토큰 발급)
```
클라이언트                     서버
   │                            │
   │  POST /api/accounts/login/ │
   │  { username, password }    │
   │ ──────────────────────────>│
   │                            │
   │         TokenObtainPairView│
   │         (simplejwt 제공)    │
   │                            │
   │  { access, refresh }       │
   │ <──────────────────────────│
```

**이 단계에서 REST_FRAMEWORK 설정은 사용되지 않음**
- `TokenObtainPairView`가 직접 토큰 생성

---

### Step 2: 인증이 필요한 API 호출
```
클라이언트                     서버
   │                            │
   │  GET /api/my-profile/      │
   │  Authorization: Bearer ... │
   │ ──────────────────────────>│
   │                            │
   │         ↓                  │
   │    REST_FRAMEWORK 설정     │
   │    "JWTAuthentication 사용"│
   │         ↓                  │
   │    JWTAuthentication 클래스│
   │    1. 토큰 추출            │
   │    2. 토큰 검증            │
   │    3. 사용자 조회          │
   │    4. request.user 설정    │
   │         ↓                  │
   │    View 함수 실행          │
   │         ↓                  │
   │  { user 정보 }             │
   │ <──────────────────────────│
```

**이 단계에서 REST_FRAMEWORK 설정이 작동**
- 모든 API 요청마다 자동으로 JWT 인증 수행

---

## 5. REST_FRAMEWORK 설정 옵션 상세

### 우리가 사용한 설정
```python
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
}
```

### 다른 설정 예시

#### 예시 1: 여러 인증 방식 병행
```python
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',  # JWT
        'rest_framework.authentication.SessionAuthentication',        # 세션
    ],
}
```
**의미**: JWT 토큰 또는 세션 쿠키 둘 다 허용

#### 예시 2: 권한 설정 추가
```python
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',  # 기본적으로 로그인 필요
    ],
}
```
**의미**: 모든 API가 기본적으로 인증된 사용자만 접근 가능

#### 예시 3: 인증 없이 모두 허용
```python
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',  # 누구나 접근 가능
    ],
}
```

---

## 6. 코드 흐름 상세 분석

### 시나리오: 사용자 프로필 조회

#### View 코드
```python
# accounts/views.py
from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(['GET'])
def my_profile(request):
    # 이 시점에 request.user는 어떻게 채워질까?
    user = request.user
    return Response({
        'username': user.username,
        'email': user.email,
    })
```

#### 내부 동작 순서
```
1. 클라이언트 요청:
   GET /api/my-profile/
   Authorization: Bearer eyJ0eXAiOiJKV1Qi...

2. Django 미들웨어 처리

3. DRF가 REST_FRAMEWORK 설정 읽기:
   "DEFAULT_AUTHENTICATION_CLASSES에 JWTAuthentication이 있네!"

4. JWTAuthentication.authenticate(request) 실행:

   class JWTAuthentication:
       def authenticate(self, request):
           # 1. Authorization 헤더 확인
           header = request.META.get('HTTP_AUTHORIZATION')
           # "Bearer eyJ0eXAiOiJKV1Qi..."

           # 2. 토큰 추출
           token = header.split(' ')[1]
           # "eyJ0eXAiOiJKV1Qi..."

           # 3. 토큰 검증 (만료, 서명 확인)
           try:
               payload = jwt.decode(token, SECRET_KEY)
           except jwt.ExpiredSignatureError:
               raise AuthenticationFailed('토큰 만료')

           # 4. 토큰에서 user_id 추출
           user_id = payload['user_id']

           # 5. DB에서 사용자 조회
           user = User.objects.get(id=user_id)

           # 6. (user, token) 반환
           return (user, token)

5. DRF가 request.user에 사용자 설정:
   request.user = user  # 4단계에서 반환된 user

6. View 함수 실행:
   my_profile(request)
   # request.user는 이미 인증된 사용자 객체!
```

---

## 7. 핵심 질문 정리

### Q1: rest_framework_simplejwt는 DRF의 플러그인인가요?
**A**: 네, 맞습니다. DRF의 서드파티 플러그인으로 JWT 인증 기능을 제공합니다.

### Q2: REST_FRAMEWORK는 장고의 기본 문법인가요?
**A**: 아니요, Django REST Framework 패키지의 설정을 담는 딕셔너리입니다.

### Q3: REST_FRAMEWORK로 로그인 기능을 연결하나요?
**A**: 부분적으로 맞습니다. 정확히는:
- **로그인 (토큰 발급)**: `TokenObtainPairView`가 처리
- **인증 (토큰 검증)**: `REST_FRAMEWORK` 설정의 `JWTAuthentication`이 처리

---

## 8. 비교: 설정 있을 때 vs 없을 때

### REST_FRAMEWORK 설정이 없다면?

```python
# settings.py (설정 없음)
# REST_FRAMEWORK = {...}  ← 주석 처리

# views.py
@api_view(['GET'])
def my_profile(request):
    print(request.user)  # AnonymousUser (익명 사용자)
    # 토큰이 있어도 인증되지 않음!
```

### REST_FRAMEWORK 설정이 있다면?

```python
# settings.py
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
}

# views.py
@api_view(['GET'])
def my_profile(request):
    print(request.user)  # User 객체 (인증된 사용자)
    # 토큰이 자동으로 검증되어 사용자 정보 제공!
```

---

## 9. 전체 구조 요약

```
┌─────────────────────────────────────────────────────────┐
│                    Django Project                        │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  ┌─────────────────────────────────────────────────┐   │
│  │           Django REST Framework (DRF)            │   │
│  │                                                   │   │
│  │  설정: REST_FRAMEWORK = {                        │   │
│  │    'DEFAULT_AUTHENTICATION_CLASSES': [...]       │   │
│  │  }                                                │   │
│  │                                                   │   │
│  │  ┌──────────────────────────────────────────┐  │   │
│  │  │  rest_framework_simplejwt (플러그인)      │  │   │
│  │  │                                            │  │   │
│  │  │  설정: SIMPLE_JWT = {                     │  │   │
│  │  │    'ACCESS_TOKEN_LIFETIME': ...,          │  │   │
│  │  │  }                                         │  │   │
│  │  │                                            │  │   │
│  │  │  제공 기능:                                │  │   │
│  │  │  - JWTAuthentication (인증 클래스)        │  │   │
│  │  │  - TokenObtainPairView (로그인 뷰)        │  │   │
│  │  │  - TokenRefreshView (토큰 갱신 뷰)        │  │   │
│  │  └──────────────────────────────────────────┘  │   │
│  └─────────────────────────────────────────────────┘   │
│                                                           │
└─────────────────────────────────────────────────────────┘
```

### 역할 분담

| 컴포넌트 | 역할 | 파일 |
|---------|------|------|
| Django | 웹 프레임워크 기본 기능 | - |
| DRF | API 구축, 인증/권한 시스템 | `REST_FRAMEWORK` 설정 |
| simplejwt | JWT 토큰 생성/검증 | `SIMPLE_JWT` 설정 |

---

## 10. 추가 학습 자료

### 관련 개념
1. **미들웨어**: Django 요청/응답 처리 파이프라인
2. **데코레이터**: `@api_view`, `@permission_classes`
3. **클래스 기반 뷰**: `TokenObtainPairView.as_view()`

### 더 알아보기
- [DRF 인증 공식 문서](https://www.django-rest-framework.org/api-guide/authentication/)
- [simplejwt 공식 문서](https://django-rest-framework-simplejwt.readthedocs.io/)
