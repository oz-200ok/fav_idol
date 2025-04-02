from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsAdminOrReadOnly(BasePermission):
    """
    관리자 등급은 쓰기 권한, 일반 유저는 읽기 권한만 부여
    """

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True  # 모두 읽기 허용
        return request.user and request.user.is_admin


class IsSuperUser(BasePermission):
    """
    요청한 사용자가 슈퍼유저인지 확인
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_superuser
