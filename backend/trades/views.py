from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django.shortcuts import get_object_or_404
from .models import Trade
from .serializers import TradeSerializer, TradeDetailSerializer
from .permissions import IsOwnerOrReadOnly  # 1. 권한 가져오기 (게시글 삭제를 위함)
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView

# generices를 쓰지 않고 기본 APIView 만 썼으면 머리는 좋아지나 효율이 안좋아질뻔;;
# 여기엔 DRF가 미리 만들어둔 클래스가 많음
# 아쉽게도 rest-framework에 있는게 아니네
# class TradeListCreateView(generics.ListCreateAPIView):
class TradeListCreateView(ListCreateAPIView):
    """게시글 목록 조회 및 등록"""
    # GET, POST 요청만 받을 수 있음
    # 최신 생성 글부터 확인
    queryset = Trade.objects.all().order_by('-created_at')
    serializer_class = TradeSerializer
    permission_classes = [IsAuthenticatedOrReadOnly] # 조회는 누구나, 등록은 로그인 유저만

    def perform_create(self, serializer):
        # 평점 등록 때처럼, 로그인한 유저를 판매자로 강제 지정!
        serializer.save(user=self.request.user)


# class TradeDetailView(generics.RetrieveUpdateDestroyAPIView):
class TradeDetailView(RetrieveUpdateDestroyAPIView):
    """게시글 상세 조회, 수정, 삭제"""
    # GET, PUT, PATCH, DELETE 요청 받을 수 있음 (POST X)
    queryset = Trade.objects.all()
    serializer_class = TradeDetailSerializer
    # permission_classes = [IsAuthenticatedOrReadOnly]
    # 2. 권한 변경: 로그인 여부만 체크하는 게 아니라 "본인 확인"까지 함
    # django rest-framework 에서는 작성자 본인 확인 기능까지는 제공하지 않기에 permissions.py
    # 에서 본인 확인이 필요함
    permission_classes = [IsOwnerOrReadOnly]
    # urls.py에서 variable routing으로 <int:id>를 사용했기에 id를 사용해서
    # 글을 찾겠다는 뜻
    lookup_field = 'id'
    # [조회] GET 요청이 오면 이 함수가 실행됨
    # HTTP method 와 함수의 연결 관계
    # 1. GET : retrieve
    # 2. PUT : update
    # 3. PATCH : partial_update
    # 4. DELETE : destroy
    def retrieve(self, request, *args, **kwargs):
        # 1. URL의 id값으로 게시글 객체를 가져옵니다.
        instance = self.get_object()
        print(instance)
        # 2. 조회수를 1 증가시키고 저장합니다.
        instance.view_count += 1
        instance.save()
        
        # 3. 상세 페이지용 시리얼라이저에 객체를 넣어 데이터를 만듭니다.
        serializer = self.get_serializer(instance)
        
        # 4. 최종 데이터를 응답합니다.
        return Response(serializer.data)

    # [삭제] DELETE 요청이 오면? 
    # 우리가 따로 안 적어도 부모 클래스(DestroyAPIView)가 
    # 내부적으로 'destroy' 함수를 실행해서 DB에서 싹 지워줍니다.

