from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Agency, Group, Idol

User = get_user_model()


class AgencyGroupIdolTests(TestCase):
    def setUp(self):
        # 슈퍼유저 생성
        self.admin_user = User.objects.create_superuser(
            name="admin",
            username="admin@admin.com",
            email="admin@admin.com",
            password="test@1234",
        )

        # 로그인
        logged_in = self.client.login(email="admin@admin.com", password="test@1234")
        self.assertTrue(
            logged_in, "Test client failed to log in with admin credentials."
        )

        # 소속사(Agency) 생성
        self.agency = Agency.objects.create(
            name="SM Entertainment",
            contact="010-1234-5678",
            image_name="sm_logo",
            image_url="http://example.com/sm_logo.png",
            image_ext="png",
        )

        # 그룹(Group) 생성
        self.group = Group.objects.create(
            agency=self.agency,
            name="EXO",
            sns="http://twitter.com/exo",
            color="black",
            image_name="exo_logo",
            image_url="http://example.com/exo_logo.png",
            image_ext="jpg",
        )

        # 아이돌(Idol) 생성
        self.idol = Idol.objects.create(
            group=self.group,
            name="Baekhyun",
            image_name="baekhyun_pic",
            image_url="http://example.com/baekhyun_pic.png",
            image_ext="png",
        )

    def test_agency_creation(self):
        # 소속사가 잘 생성되었는지 확인
        self.assertEqual(self.agency.name, "SM Entertainment")
        self.assertEqual(self.agency.contact, "010-1234-5678")
        self.assertEqual(self.agency.image_url, "http://example.com/sm_logo.png")

    def test_group_creation(self):
        # 그룹이 잘 생성되었는지 확인
        self.assertEqual(self.group.name, "EXO")
        self.assertEqual(self.group.agency, self.agency)
        self.assertEqual(self.group.image_url, "http://example.com/exo_logo.png")

    def test_idol_creation(self):
        # 아이돌이 잘 생성되었는지 확인
        self.assertEqual(self.idol.name, "Baekhyun")
        self.assertEqual(self.idol.group, self.group)
        self.assertEqual(self.idol.image_url, "http://example.com/baekhyun_pic.png")

    def test_inline_relationships(self):
        # Group이 Agency와 연결되었는지 확인
        self.assertEqual(self.group.agency.name, "SM Entertainment")

        # Idol이 Group과 연결되었는지 확인
        self.assertEqual(self.idol.group.name, "EXO")

    def test_admin_urls(self):
        # 관리자 페이지 URL 확인
        agency_list_url = reverse("admin:Idols_agency_changelist")
        group_list_url = reverse("admin:Idols_group_changelist")
        idol_list_url = reverse("admin:Idols_idol_changelist")

        response_agency = self.client.get(agency_list_url)
        response_group = self.client.get(group_list_url)
        response_idol = self.client.get(idol_list_url)

        self.assertEqual(response_agency.status_code, 200)  # 소속사 리스트 페이지
        self.assertEqual(response_group.status_code, 200)  # 그룹 리스트 페이지
        self.assertEqual(response_idol.status_code, 200)  # 아이돌 리스트 페이지
