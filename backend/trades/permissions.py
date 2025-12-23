from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    객체의 작성자만 수정/삭제 가능하게 하는 권한
    """
    def has_object_permission(self, request, view, obj):
        # 조회(GET)는 누구나 가능
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # 수정(PUT, PATCH), 삭제(DELETE) 요청은 작성자(user)만 가능
        return obj.user == request.user


