from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

User = get_user_model()


class AboutTestUrls(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create_user(username="auth")

    def setUp(self) -> None:
        super().setUp()
        self.guest_client = Client()

    def test_about_author(self):
        """
        Тест страницы об авторе.
        """
        response = self.guest_client.get("/about/author/")
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_tech(self):
        """
        Тест страницы технологии.
        """
        response = self.guest_client.get("/about/tech/")
        self.assertEqual(response.status_code, HTTPStatus.OK)
