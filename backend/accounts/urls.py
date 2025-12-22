from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from . import views

app_name = 'accounts'

urlpatterns = [
    path('signup/', views.signup, name='signup'),
    # 로그인 로직은 simple-jwt가 제공하는 로그인 view함수를 사용(아이디, 비밀번호 검증 후 토큰 발급)
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('logout/', views.logout, name='logout'),
    # 토큰 재발급 요청 코드
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # 프로필 조회 및 수정
    path('profile/', views.profile, name='profile'),
    path('profile/update/', views.update_profile, name='update_profile'),
]
