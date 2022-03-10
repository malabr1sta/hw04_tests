from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from posts.models import Group, Post

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group,
        )

    def setUp(self):
        self.guest_client = Client()
        self.user = PostURLTests.user
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_anonymous_user(self):
        """Страницы доступны неавторизованному пользователю"""

        pages_addresses = [
            '/',
            '/group/test-slug/',
            '/profile/auth/',
            f'/posts/{PostURLTests.post.pk}/',
        ]
        for url in pages_addresses:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, 200)

    def test_pages_authorized_user(self):
        """Страницы доступны авторизованному пользователю,
        и страница для редоктировыния поста доступна автору поста"""

        pages_addresses = [
            '/',
            '/group/test-slug/',
            '/profile/auth/',
            f'/posts/{PostURLTests.post.pk}/',
            '/create/',
            f'/posts/{PostURLTests.post.pk}/edit/',
        ]
        for url in pages_addresses:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertEqual(response.status_code, 200)

    def test_urls_uses_correct_template(self):
        """URL-адреса использует соответствующий шаблоны."""

        template_url_names = {
            '/': 'posts/index.html',
            '/group/test-slug/': 'posts/group_list.html',
            '/profile/auth/': 'posts/profile.html',
            f'/posts/{PostURLTests.post.pk}/': 'posts/post_detail.html',
            '/create/': 'posts/create_post.html',
            f'/posts/{PostURLTests.post.pk}/edit/': 'posts/create_post.html',
        }
        for address, template in template_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_code_404_returns(self):
        """Cервер возвращает код 404, если страница не найдена."""

        response = self.guest_client.get('unexisting_page')
        self.assertEqual(response.status_code, 404)
