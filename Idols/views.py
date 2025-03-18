from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Agency, Group, Idol
from .serializers import AgencySerializer, GroupSerializer, IdolSerializer


# 에이전시 리스트
class AgencyListView(APIView):
    def get(self, request):
        agencies = Agency.objects.all()
        serializer = AgencySerializer(agencies, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = AgencySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()  # 검증된 데이터를 저장
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 그룹 리스트
class GroupListView(APIView):
    def get(self, request):
        groups = Group.objects.select_related("agency").all()
        serializer = GroupSerializer(groups, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = GroupSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 아이돌 리스트
class IdolListView(APIView):
    def get(self, request):
        idols = Idol.objects.select_related("group").all()
        serializer = IdolSerializer(idols, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = IdolSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
