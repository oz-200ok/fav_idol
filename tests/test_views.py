from django.test import Client, TestCase, override_settings
from django.urls import reverse


class TestViewExceptions(TestCase):
    @override_settings(ROOT_URLCONF="config.urls")
    def test_not_found_exception(self):
        # 뷰 호출
        response = self.client.get(reverse("test_view"))

        # 응답 상태 코드 확인
        self.assertEqual(response.status_code, 404)

        # 응답 JSON 데이터 확인
        self.assertEqual(
            response.json(),
            {
                "error_code": "not_found",
                "error_message": "테스트용 리소스 없음 오류",
                "status_code": 404,
            },
        )
