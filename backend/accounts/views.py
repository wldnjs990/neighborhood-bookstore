from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import SignupSerializer, UserSerializer, ProfileUpdateSerializer
from drf_spectacular.utils import extend_schema


@extend_schema(
    request=SignupSerializer,
    responses=UserSerializer,
    summary="회원가입",
)
@api_view(['POST'])
@permission_classes([AllowAny])
def signup(request):
    serializer = SignupSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        refresh = RefreshToken.for_user(user)

        return Response({
            'user': UserSerializer(user).data,
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# refresh 토큰 하나만 필요하기에 Serializers 없이 정보 받아옴
@extend_schema(
    request={
        "application/json": {
            "type": "object",
            "properties": {
                "refresh": {"type": "string"}
            },
            "required": ["refresh"]
        }
    },
    responses=None,
    summary="로그아웃"
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    """로그아웃 - Refresh Token을 블랙리스트에 추가"""
    try:
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response(
                {'error': 'Refresh token이 필요합니다.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 현재 토큰 가져오기
        token = RefreshToken(refresh_token)
        # 토큰 블랙리스트 등록(토큰 사용 불가 처리)
        token.blacklist()

        return Response(
            {'message': '로그아웃되었습니다.'},
            status=status.HTTP_205_RESET_CONTENT
        )
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )


@extend_schema(
    responses=UserSerializer,
    summary="내 프로필 조회"
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile(request):
    """현재 로그인한 사용자 프로필 조회"""
    serializer = UserSerializer(request.user)
    return Response(serializer.data)


@extend_schema(
    request=ProfileUpdateSerializer,
    responses=UserSerializer,
    summary="프로필 수정"
)
@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_profile(request):
    """프로필 수정 (email, nickname, age, book_mbti)"""
    serializer = ProfileUpdateSerializer(
        request.user,
        data=request.data,
        partial=True,
        context={'request': request}
    )
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
