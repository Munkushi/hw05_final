from django.contrib.auth import get_user_model
from django.test import TestCase

from posts.models import Group, Post

User = get_user_model()


class TestPostModel(TestCase):
    """
    Тест модели Post.
    """

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create_user(username="auth")
        cls.post = Post.objects.create(
            author=cls.user,
            text="Тестовая группа",
        )

    def test_models_have_correct_object_names(self):
        """
        Проверка, что у модели корректно рабоатет __str__.
        """
        post = TestPostModel.post

        self.assertEqual(self.post.text[:15], str(post))


class TestGroupModel(TestCase):
    """
    Тест модели Group.
    """

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create_user(username="auth")
        cls.group = Group.objects.create(
            title="Тестовая группа",
            slug="Тестовый слаг",
            description="Тестовое описание",
        )

    def test_model_group_have_correct_object_names(self):
        """
        Проверка, что у модели корректно рабоатет __str__.
        """
        group = TestGroupModel.group
        expected_object_group = group.title
        self.assertEqual(expected_object_group, str(group))
