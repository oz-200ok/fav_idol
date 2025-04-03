from django.db.models import Count
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.generics import (
    GenericAPIView,
    ListAPIView,
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView,
    get_object_or_404,
)
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from config.permissions import IsAdminOrReadOnly

from .models import Agency, Group, Idol
from .serializers import AgencySerializer, GroupSerializer, IdolSerializer

# from config.base_exception import NotFoundException

class TestView(GenericAPIView):
    def get(self, request, *args, **kwargs):
        raise NotFoundException("테스트용 리소스 없음 오류")


# 에이전시 리스트
class AgencyListView(ListCreateAPIView):
    queryset = Agency.objects.all()
    serializer_class = AgencySerializer
    permission_classes = [IsAdminOrReadOnly]
    parser_classes = (MultiPartParser, FormParser)

    @swagger_auto_schema(
        operation_description="소속사 목록을 가져옵니다.",
        responses={200: AgencySerializer(many=True)},  # 목록 반환
    )
    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        return Response({"data": response.data}, status=response.status_code)

    @swagger_auto_schema(
        operation_description="새 소속사를 생성합니다.",
        responses={
            201: AgencySerializer,
            400: "유효하지 않은 요청 데이터입니다.",
        },
    )
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        return Response({"data": response.data}, status=response.status_code)

    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]  # 읽기 요청은 모든 사용자 허용
        return super().get_permissions()  # 관리자만 쓰기 허용


class AgencyDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Agency.objects.all()
    serializer_class = AgencySerializer
    permission_classes = [IsAdminOrReadOnly]
    parser_classes = (MultiPartParser, FormParser)

    @swagger_auto_schema(
        operation_description="특정 소속사 데이터를 조회합니다.",
        responses={200: AgencySerializer},  # 성공 시 반환할 데이터 스키마
    )
    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        return Response({"data": response.data}, status=response.status_code)

    @swagger_auto_schema(
        operation_description="특정 소속사 데이터를 업데이트합니다.",
        request_body=AgencySerializer,  # 요청 시 필요한 데이터 스키마
        responses={
            200: AgencySerializer,  # 성공 시 반환할 데이터 스키마
            400: "요청 데이터 유효성 검사 실패",
        },
    )
    def put(self, request, *args, **kwargs):
        response = super().put(request, *args, **kwargs)
        return Response({"data": response.data}, status=response.status_code)

    @swagger_auto_schema(
        operation_description="특정 소속사 데이터를 삭제합니다.",
        responses={
            204: "데이터 삭제 성공",  # No Content 응답
            404: "소속사를 찾을 수 없습니다.",
        },
    )
    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs)
        return Response({"data": "소속사 삭제 성공"}, status=response.status_code)


# 그룹 리스트
class GroupListView(ListCreateAPIView):
    queryset = (
        Group.objects.select_related("agency")
        .prefetch_related("idol_set")
        .annotate(member_count=Count("idol"))
    )
    serializer_class = GroupSerializer
    permission_classes = [IsAdminOrReadOnly]
    parser_classes = (MultiPartParser, FormParser)

    @swagger_auto_schema(
        operation_description="그룹 목록을 가져옵니다.",
        responses={
            200: GroupSerializer(many=True),  # 그룹 목록 반환
        },
    )
    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        return Response({"data": response.data}, status=response.status_code)

    @swagger_auto_schema(
        operation_description="새 그룹을 생성합니다.",
        request_body=GroupSerializer,  # 생성 시 필요한 데이터 스키마
        responses={
            201: GroupSerializer,  # 성공적으로 생성된 그룹 반환
            400: "유효하지 않은 요청 데이터",
        },
    )
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        return Response({"data": response.data}, status=response.status_code)


class GroupByNameView(ListAPIView):
    serializer_class = GroupSerializer

    def get_queryset(self):
        name = self.kwargs["name"]  # URL에서 'name' 변수 가져오기
        # 특정 이름의 그룹 조회
        return (
            Group.objects.select_related("agency")
            .prefetch_related("idol_set")
            .filter(name=name)
            .annotate(member_count=Count("idol"))
        )

    def list(self, request, *args, **kwargs):
        # 기본 리스트 뷰 동작을 가져옴
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({"data": serializer.data}, status=200)


class GroupDetailView(RetrieveUpdateDestroyAPIView):
    queryset = (
        Group.objects.select_related("agency")
        .prefetch_related("idol_set")
        .annotate(member_count=Count("idol"))
    )
    serializer_class = GroupSerializer
    permission_classes = [IsAdminOrReadOnly]
    parser_classes = (MultiPartParser, FormParser)

    @swagger_auto_schema(
        operation_description="특정 그룹 데이터를 조회합니다.",
        responses={
            200: GroupSerializer,  # 그룹 데이터 반환
            404: "그룹을 찾을 수 없습니다.",
        },
    )
    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        return Response({"data": response.data}, status=response.status_code)

    @swagger_auto_schema(
        operation_description="특정 그룹 데이터를 업데이트합니다.",
        request_body=GroupSerializer,  # 업데이트 요청 데이터
        responses={
            200: GroupSerializer,  # 업데이트된 그룹 데이터 반환
            400: "유효하지 않은 요청 데이터",
        },
    )
    def put(self, request, *args, **kwargs):
        response = super().put(request, *args, **kwargs)
        return Response({"data": response.data}, status=response.status_code)

    @swagger_auto_schema(
        operation_description="특정 그룹 데이터를 삭제합니다.",
        responses={
            204: "그룹 삭제 성공",
            404: "그룹을 찾을 수 없습니다.",
        },
    )
    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs)
        return Response({"data": "그룹 삭제 성공"}, status=response.status_code)


# 아이돌 리스트
class IdolListView(ListCreateAPIView):
    queryset = Idol.objects.select_related("group")
    serializer_class = IdolSerializer
    permission_classes = [IsAdminOrReadOnly]
    parser_classes = (MultiPartParser, FormParser)

    @swagger_auto_schema(
        operation_description="아이돌 목록을 가져옵니다.",
        responses={
            200: IdolSerializer(many=True),  # 아이돌 목록 반환
        },
    )
    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        return Response({"data": response.data}, status=response.status_code)

    @swagger_auto_schema(
        operation_description="개별 아이돌을 생성합니다.",
        request_body=IdolSerializer,  # 생성 시 필요한 데이터 스키마
        responses={
            201: IdolSerializer,  # 생성된 아이돌 반환
            400: "유효하지 않은 요청 데이터",
        },
    )
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        return Response({"data": response.data}, status=response.status_code)


class IdolDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Idol.objects.select_related("group")
    serializer_class = IdolSerializer
    parser_classes = (MultiPartParser, FormParser)

    @swagger_auto_schema(
        operation_description="특정 아이돌 데이터를 조회합니다.",
        responses={
            200: IdolSerializer,  # 성공 시 아이돌 데이터 반환
            404: "아이돌을 찾을 수 없습니다.",
        },
    )
    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        return Response({"data": response.data}, status=response.status_code)

    @swagger_auto_schema(
        operation_description="특정 아이돌 데이터를 업데이트합니다.",
        request_body=IdolSerializer,  # 요청 시 필요한 데이터 스키마
        responses={
            200: IdolSerializer,  # 성공 시 업데이트된 데이터 반환
            400: "유효하지 않은 요청 데이터",
        },
    )
    def put(self, request, *args, **kwargs):
        response = super().put(request, *args, **kwargs)
        return Response({"data": response.data}, status=response.status_code)

    @swagger_auto_schema(
        operation_description="특정 아이돌 데이터를 삭제합니다.",
        responses={
            200: openapi.Response(
                description="삭제된 아이돌 데이터",
                examples={
                    "application/json": {
                        "data": {
                            "idol.id": 1,
                            "group_id": 2,
                            "name": "아이돌 이름",
                        }
                    }
                },
            ),
            404: "아이돌을 찾을 수 없습니다.",
        },
    )
    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        deleted_idol_data = {
            "idol.id": instance.id,
            "group_id": instance.group_id,
            "name": instance.name,
        }
        self.perform_destroy(instance)
        return Response({"data": deleted_idol_data}, status=status.HTTP_200_OK)
