from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Group, Post

User = get_user_model()


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        for i in range(13):
            Post.objects.create(
                author=cls.user,
                text=f'Тестовый пост_{i}',
                group=cls.group,
            )

    def setUp(self):
        self.guest_client = Client()

    def test_first_page_contains_ten_records(self):
        pages_addresses = [
            reverse('posts:index'),
            reverse(
                'posts:group_list',
                kwargs={'slug': PaginatorViewsTest.group.slug},
            ),
            reverse(
                'posts:profile',
                kwargs={'username': PaginatorViewsTest.user.username},
            ),
        ]
        for reverse_name in pages_addresses:
            with self.subTest(reverse_name=reverse_name):
                response = self.client.get(reverse_name)
                self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_page_contains_ten_records(self):
        pages_addresses = [
            reverse('posts:index'),
            reverse(
                'posts:group_list',
                kwargs={'slug': PaginatorViewsTest.group.slug},
            ),
            reverse(
                'posts:profile',
                kwargs={'username': PaginatorViewsTest.user.username},
            ),
        ]
        for reverse_name in pages_addresses:
            with self.subTest(reverse_name=reverse_name):
                response = self.client.get(reverse_name + '?page=2')
                self.assertEqual(len(response.context['page_obj']), 3)
