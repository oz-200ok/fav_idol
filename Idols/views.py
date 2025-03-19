from django.db.models import Count
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Agency, Group, Idol
from .permissions import IsAdminOrReadOnly, IsSuperUser
from .serializers import AgencySerializer, GroupSerializer, IdolSerializer


# 에이전시 리스트
class AgencyListView(APIView):
    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]  # 읽기는 모든 유저 허용
        return [IsSuperUser()]  # Post/Delete는 슈퍼유저만 허용

    def get(self, request):
        agencies = Agency.objects.all()
        serializer = AgencySerializer(agencies, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    permission_classes = [IsSuperUser]

    def post(self, request):
        serializer = AgencySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()  # 검증된 데이터를 저장
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        agency = get_object_or_404(Agency, pk=pk)
        agency.delete()
        return Response(
            {"message": "소속사가 삭제되었습니다."}, status=status.HTTP_200_OK
        )


# 그룹 리스트
class GroupListView(APIView):
    permission_classes = [IsAdminOrReadOnly]

    def get(self, request):
        groups = Group.objects.select_related("agency").annotate(
            member_count=Count("idol")
        )
        serializer = GroupSerializer(groups, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = GroupSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk=None):
        group = get_object_or_404(Group, pk=pk)
        group.delete()
        return Response(
            {"message": "그룹 삭제가 완료되었습니다."}, status=status.HTTP_200_OK
        )


# 아이돌 리스트
class IdolListView(APIView):
    permission_classes = [IsAdminOrReadOnly]

    def get(self, request):
        idols = Idol.objects.select_related("group").all()
        serializer = IdolSerializer(idols, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # 아이돌 리스트 동일 적용
    def post(self, request):
        serializer = IdolSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk=None):
        idol = get_object_or_404(Idol, pk=pk)
        idol.delete()
        return Response(
            {"message": "요청하신 아이돌 삭제가 완료되었습니다."},
            status=status.HTTP_200_OK,
        )
