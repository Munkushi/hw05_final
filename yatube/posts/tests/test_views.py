import shutil
import tempfile

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.forms import PostForm
from posts.models import Comment, Group, Post

User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostPagesTests(TestCase):
    """
    Тест страниц приложения Post
    """

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create_user(username="auth")
        cls.group = Group.objects.create(
            title="Тестовая группа",
            slug="test-slug",
            description="Тестовое описание",
        )
        cls.group33 = Group.objects.create(
            title="test_group", slug="test-slug3", description="test_descr"
        )
        cls.small_png = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.png', content=cls.small_png, content_type="image/png"
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text="Тестовый пост",
            group=cls.group,
            image=cls.uploaded,
        )
        cls.form_data = {
            "post": forms.fields.ChoiceField,
            "group": forms.fields.ChoiceField,
            "image": forms.fields.ImageField,
        }

    @classmethod
    def tearDownClass(cls) -> None:
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self) -> None:
        cache.clear()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.comment = Comment.objects.create(
            post=self.post, author=self.user, text="Текст коммента"
        )

    def test_urls_correct_html_guest_client(self):
        """
        Во view функциях используются правильные html-шаблоны для гостя.
        """
        template_html = {
            "posts/index.html": reverse("posts:index"),
            "posts/group_list.html": reverse(
                "posts:group_posts", kwargs={"slug": self.group.slug}
            ),
            "posts/profile.html": reverse(
                "posts:profile", args=(self.user.username,)
            ),
            "posts/post_detail.html": reverse(
                "posts:post_detail", kwargs={"post_id": self.post.pk}
            ),
        }

        for template, url in template_html.items():
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertTemplateUsed(response, template)

    def test_urls_for_create_correct_html(self):
        """
        Для create-функции используется правильный шаблон.
        """
        response = self.authorized_client.get(reverse("posts:post_create"))
        self.assertTemplateUsed(response, "posts/create_post.html")

    def test_urls_for_edit_correct_html(self):
        """
        Для edit-функции используется правильный шаблон.
        """
        response = self.authorized_client.get(
            reverse("posts:post_edit", kwargs={"post_id": self.post.pk})
        )
        self.assertTemplateUsed(response, "posts/create_post.html")

    def test_index_show_correct_context(self):
        """
        На странице index сформирован правильный context.
        """
        response = self.client.get(reverse("posts:index"))
        first_object = response.context["page_obj"][0]
        post_author_0 = first_object.author
        post_text_0 = first_object.text
        post_group_0 = first_object.group
        post_image_0 = first_object.image
        self.assertEqual(post_author_0, self.post.author)
        self.assertEqual(post_text_0, self.post.text)
        self.assertEqual(post_group_0, self.group)
        self.assertEqual(post_image_0, self.post.image)

    def test_create_post_show_correct_context(self):
        """
        На странице create_post сформирован правильный context.
        """
        response = self.authorized_client.get(reverse("posts:post_create"))
        self.assertIsInstance(response.context.get("form"), PostForm)
        self.assertFalse(response.context["is_edit"])

    def test_edit_post_show_correct_context(self):
        """
        На странице edit_post сформирован правильный context.
        """
        response = self.authorized_client.get(
            reverse("posts:post_edit", kwargs={"post_id": self.post.pk})
        )
        self.assertIsInstance(response.context.get("form"), PostForm)
        self.assertTrue(response.context["is_edit"])

    def post_detail_show_correct_context(self):
        """
        На странице post_detail сформирован правильный context.
        """
        response = self.client.get(
            reverse("posts:post_detail", kwargs={"post_id": self.post.pk})
        )
        first_object_0 = response.context["page_obj"][0]
        post_comment = response.context.get("comments")[0]
        post_author_0 = first_object_0.author
        post_text_0 = first_object_0.text
        post_group_0 = first_object_0.group
        post_image_0 = first_object_0.image
        post_comment_0 = post_comment.text
        self.assertEqual(post_author_0, self.post.author)
        self.assertEqual(post_text_0, self.post.text)
        self.assertEqual(post_group_0, self.group)
        self.assertEqual(post_image_0, self.post.image)
        self.assertEqual(post_comment_0, self.comment.text)

    def test_profile_show_correct_context(self):
        """
        На странице профиля правильный context.
        """
        response = self.authorized_client.get(
            reverse("posts:profile", args=(PostPagesTests.user.username,))
        )
        post = self.post
        author = post.author
        filter_for_author = response.context.get("author")
        self.assertEqual(filter_for_author, author)

    def test_group_list_show_correct_context(self):
        """
        На странице group_list сформирован правильный context.
        """
        response = self.client.get(
            reverse("posts:group_posts", kwargs={"slug": self.group.slug})
        )

        first_object = response.context["page_obj"][0]
        post_author_2 = first_object.author
        post_text_2 = first_object.text
        post_group_2 = first_object.group
        post_image_2 = first_object.image
        self.assertEqual(post_author_2, self.post.author)
        self.assertEqual(post_text_2, self.post.text)
        self.assertEqual(post_group_2, self.group)
        self.assertEqual(post_image_2, self.post.image)

    def test_new_post_appears_on_group(self):
        """
        У поста нужная группа.
        """
        response = self.client.get(
            reverse("posts:group_posts", args=[self.group.slug])
        )
        self.assertIn(self.post, response.context.get("page_obj"))

    def test_post_appears_in_index(self):
        """
        Пост появляется на главной странице.
        """
        response = self.client.get(reverse("posts:index"))
        self.assertIn(self.post, response.context.get("page_obj"))

    def test_post_appears_in_profile(self):
        """
        Пост появляется в профиле.
        """
        response = self.client.get(
            reverse("posts:profile", args=[PostPagesTests.user.username])
        )
        self.assertIn(self.post, response.context.get("page_obj"))

    def test_post_not_in_group(self):
        """
        Пост не появляется в нужной группе.
        """
        response = self.client.get(
            reverse("posts:group_posts", kwargs={"slug": self.group33.slug})
        )
        self.assertNotIn(self.post, response.context.get("page_obj"))

    def test_index_cache(self):
        """
        Тестирование кеша.
        """
        response = self.client.get(reverse("posts:index"))
        Post.objects.filter(id=PostPagesTests.post.id).delete()
        self.assertIn(self.post.text, response.content.decode("utf-8"))
        cache.clear()
        response = self.client.get(reverse("posts:index"))
        self.assertNotIn(self.post.text, response.content.decode("utf-8"))


class Follow(classmethod):
    """
    Подписка/отписка.
    """

    @classmethod
    def setUpClass(cls) -> None:
        cls.user = User.objects.create_user(username="auth")
        cls.author = User.objects.create_user(username="Kate")
        cls.group = Group.objects.create(
            title="Тестовая группа",
            slug="test-slug",
            description="Тестовое описание",
        )
        cls.group33 = Group.objects.create(
            title="test_group", slug="test-slug3", description="test_descr"
        )

        cls.post = Post.objects.create(
            author=cls.user,
            text="Тестовый пост",
            group=cls.group,
            image=cls.uploaded,
        )
        cls.form_data = {
            "post": forms.fields.ChoiceField,
        }
        cls.follow = Follow.objects.create(author=cls.user2, user=cls.user)

    def setUp(self) -> None:
        cache.clear()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_follow_unfollow(self):
        """
        Тест подписки/отписки.
        """

        count_follow = Follow.objects.filter(
            author=self.user2, user=self.user
        ).count()
        count_unfollow = Follow.objects.filter(
            author=self.user, user=self.user2
        ).count()
        self.assertEqual(count_follow, 1)
        self.assertEqual(count_unfollow, 0)

    def test_followed_author_can_see_post(self):
        """
        Автор видит посты от подписанных авторов.
        """

        response = self.authorized_client.get(reverse("posts:follow_index"))
        post_followed = Post.objects.create(
            author=self.follow.user,
            text="follow_test",
            group=self.group,
            image=self.uploaded,
        )
        self.assertIn(post_followed, response.context.get["page_obj"])
        self.assertRedirects(
            response, reverse("posts:profile", args=[self.user.username])
        )

    def test_unfollowed_can_not_see_post(self):
        """
        Не видит посты, если не подписан.
        """

        response = self.authorized_client.get(reverse("posts:follow_index"))
        post_unfollowed = Post.objects.create(
            author=self.post.author,
            text="invisible",
            group=self.group,
            image=self.uploaded,
        )

        self.assertNotIn(post_unfollowed, response.context.get["page_obj"])

    class PaginatorViewTest(TestCase):
        """
        Тест паджинатора.
        """

        @classmethod
        def setUpClass(cls) -> None:
            super().setUpClass()
            cache.clear()
            cls.author = User.objects.create_user(
                username="test_user4paginator"
            )
            cls.authorized_client = Client()
            cls.authorized_client.force_login(cls.author)
            cls.group = Group.objects.create(
                title="new group", slug="new-slug", description="new text"
            )
            for i in range(1, 14):
                cls.post = Post.objects.create(
                    author=cls.author,
                    text="Тест текст для паджинатора",
                    group=cls.group,
                )
            cls.dict_for_paginator = {
                1: reverse("posts:index"),
                2: reverse("posts:group_posts", args=(cls.group.slug,)),
                3: reverse(
                    "posts:profile", kwargs={"username": cls.author.username}
                ),
            }

        def test_first_page_contains_ten_records(self):
            """
            Количество постов на первой странице равно 10.
            """
            for i in self.dict_for_paginator:
                with self.subTest(i=i):
                    response = self.client.get(self.dict_for_paginator[i])
                    self.assertEqual(
                        len(response.context["page_obj"].object_list),
                        settings.PAGINATOR_NUM,
                    )

        def test_second_page_contains_ten_records(self):
            """
            Количество постов на второй странице равно 3.
            """
            for i in self.dict_for_paginator:
                with self.subTest(i=i):
                    response = self.client.get(
                        self.dict_for_paginator[i] + "?page=2"
                    )
                    self.assertEqual(
                        len(response.context["page_obj"].object_list),
                        3,
                    )
