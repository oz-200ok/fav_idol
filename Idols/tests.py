from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Agency, Group, Idol


class AgencyViewTests(APITestCase):
    def setUp(self):
        # 테스트 데이터 생성
        self.agency = Agency.objects.create(name="Test Agency", contact="123456789")
        self.agency_list_url = reverse("agency-list")
        self.agency_detail_url = reverse("agency-detail", kwargs={"pk": self.agency.id})

    def test_get_agency_list(self):
        """소속사 목록 조회 테스트"""
        response = self.client.get(self.agency_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue("data" in response.data)

    def test_create_agency(self):
        """소속사 생성 테스트"""
        data = {
            "name": "New Agency",
            "contact": "987654321",
        }
        response = self.client.post(self.agency_list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Agency.objects.count(), 2)
        self.assertEqual(Agency.objects.last().name, "New Agency")

    def test_get_agency_detail(self):
        """소속사 상세 조회 테스트"""
        response = self.client.get(self.agency_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["data"]["name"], self.agency.name)

    def test_update_agency(self):
        """소속사 업데이트 테스트"""
        data = {"name": "Updated Agency", "contact": "111222333"}
        response = self.client.put(self.agency_detail_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Agency.objects.get(id=self.agency.id).name, "Updated Agency")

    def test_delete_agency(self):
        """소속사 삭제 테스트"""
        response = self.client.delete(self.agency_detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Agency.objects.count(), 0)