from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase

from posts.models import Group, Post

User = get_user_model()


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create_user(username="auth")
        cls.group = Group.objects.create(
            title="Тестовая группа",
            slug="test-slug",
            description="Тестовое описание",
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text="Тестовый пост",
            group=cls.group,
        )

    def setUp(self):
        self.author = User.objects.create_user(username="Alex")
        self.user2 = User.objects.create_user(username="John")
        self.post = Post.objects.create(
            author=self.user2, text="Тестовый пост11_user2", group=self.group
        )
        cache.clear()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.author)

    def test_urls_uses_correct_template(self):
        """
        Url шаблонов
        """
        templates_url_names = {
            "/": "posts/index.html",
            f"/group/{self.group.slug}/": "posts/group_list.html",
            f"/profile/{self.user.username}/": "posts/profile.html",
            f"/posts/{self.post.pk}/": "posts/post_detail.html",
        }

        for url, template in templates_url_names.items():
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertTemplateUsed(response, template)

    def url_for_edit_200(self):
        """
        Url имеет правильный шаблон.
        """
        response = self.authorized_client_author.get(
            f"/posts/{self.post.id}/edit/"
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def urls_for_create_200(self):
        """
        Url имеет правильный шаблон.
        """
        response = self.authorized_client_author.get('/create/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_unexisting_page(self):
        """
        Url имеет правильный шаблон.
        """
        response = self.client.get("/posts/nettakoystranizi/")
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_follow_url(self):
        """
        Url имеет правильный шаблон.
        """

        response = self.authorized_client.get("/follow/")
        self.assertEqual(response.status_code, HTTPStatus.OK)
