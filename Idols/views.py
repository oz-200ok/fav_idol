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
        return Response({"data": serializer.data}, status=status.HTTP_200_OK)

    permission_classes = [IsSuperUser]

    def post(self, request):
        serializer = AgencySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()  # 검증된 데이터를 저장
            return Response({"data": serializer.data}, status=status.HTTP_201_CREATED)
        return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        agency = get_object_or_404(Agency, pk=pk)
        deleted_data = {
            "id": agency.id,
            "name": agency.name
        }
        agency.delete()
        return Response({"data":deleted_data}, status=status.HTTP_200_OK)

# 그룹 리스트
class GroupListView(APIView):
    permission_classes = [IsAdminOrReadOnly]

    def get(self, request):
        groups = Group.objects.select_related("agency").annotate(
            member_count=Count("idol")
        )
        serializer = GroupSerializer(groups, many=True)
        return Response({"data": serializer.data}, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = GroupSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"data": serializer.data}, status=status.HTTP_201_CREATED)
        return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        group = get_object_or_404(Group, pk=pk)
        deleted_data = {
            "id": group.id,
            "agency_name": group.agency.name,
            "name": group.name,
        }
        group.delete()
        return Response({"data":deleted_data}, status=status.HTTP_200_OK)

# 아이돌 리스트
class IdolListView(APIView):
    permission_classes = [IsAdminOrReadOnly]

    def get(self, request):
        idols = Idol.objects.select_related("group").all()
        serializer = IdolSerializer(idols, many=True)
        return Response({"data": serializer.data}, status=status.HTTP_200_OK)

    # 아이돌 리스트 동일 적용
    def post(self, request):
        serializer = IdolSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"data":serializer.data}, status=status.HTTP_201_CREATED)
        return Response({"error":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        idol = get_object_or_404(Idol, pk=pk)

        deleted_data = {
            "id": idol.id,
            "name": idol.name,
            "group_id": idol.group_id,
        }

        # 객체 삭제
        idol.delete()
        return Response({"data":deleted_data}, status=status.HTTP_200_OK)