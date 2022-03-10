from django import forms
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Group, Post

User = get_user_model()


class PostPagesTests(TestCase):
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
        self.user = PostPagesTests.user
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""

        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_list',
                kwargs={'slug': PostPagesTests.group.slug},
            ): 'posts/group_list.html',
            reverse(
                'posts:profile',
                kwargs={'username': PostPagesTests.user.username},
            ): 'posts/profile.html',
            reverse(
                'posts:post_detail',
                kwargs={'post_id': PostPagesTests.post.pk},
            ): 'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse(
                'posts:post_edit',
                kwargs={'post_id': PostPagesTests.post.pk},
            ): 'posts/create_post.html',
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_profile_show_correct_context(self):
        """Шаблоны index, profile сформированы с правильным контекстом."""

        expected_post = PostPagesTests.post
        pages_addresses = [
            reverse('posts:index'),
            reverse(
                'posts:profile',
                kwargs={'username': PostPagesTests.user.username},
            ),
        ]
        for reverse_name in pages_addresses:
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                actual_post = response.context['page_obj'][0]
                self.assertEqual(actual_post, expected_post)

    def test_page_post_detail_show_correct_context(self):
        """Шаблон detail сформирован с правильным контекстом."""

        reverse_name = reverse(
            'posts:post_detail',
            kwargs={'post_id': PostPagesTests.post.pk},
        )
        response = self.authorized_client.get(reverse_name)
        expected_post = PostPagesTests.post
        actual_post = response.context['post']
        self.assertEqual(actual_post, expected_post)

    def test_page_group_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""

        reverse_name = reverse(
            'posts:group_list',
            kwargs={'slug': PostPagesTests.group.slug},
        )
        response = self.authorized_client.get(reverse_name)
        expected_post = PostPagesTests.group
        actual_post = response.context['group']
        self.assertEqual(actual_post, expected_post)

    def test_page_post_create_edit_show_correct_context(self):
        """Шаблоны create, edit сформированы с правильным контекстом."""

        pages_addresses = [
            reverse('posts:post_create'),
            reverse(
                'posts:post_edit',
                kwargs={'post_id': PostPagesTests.post.pk},
            ),
        ]
        form_fields = {
            'group': forms.ChoiceField,
            'text': forms.CharField,
        }
        for reverse_name in pages_addresses:
            for value, expected in form_fields.items():
                with self.subTest(value=value):
                    response = self.authorized_client.get(reverse_name)
                    actual = response.context.get('form').fields.get(value)
                    self.assertIsInstance(actual, expected)

    def test_post_apper_in_pages(self):
        """Пост появился на главной странице,
        на странице выбранной группы, в профайле пользователя"""

        expected_post = PostPagesTests.post
        pages_addresses = [
            reverse('posts:index'),
            reverse(
                'posts:group_list',
                kwargs={'slug': PostPagesTests.group.slug},
            ),
            reverse(
                'posts:profile',
                kwargs={'username': PostPagesTests.user.username},
            ),
        ]
        for reverse_name in pages_addresses:
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertContains(response, expected_post)

    def test_post_not_in_other_group(self):
        """Пост не попал в группу, для которой не был предназначен"""

        post = PostPagesTests.post
        self.group = Group.objects.create(
            title='Тестовое описание второе',
            slug='test-slug_2',
            description='Тестовое описание второе',
        )
        revers_name = reverse(
            'posts:group_list',
            kwargs={'slug': self.group.slug},
        )
        response = self.authorized_client.get(revers_name)
        self.assertNotContains(response, post)
