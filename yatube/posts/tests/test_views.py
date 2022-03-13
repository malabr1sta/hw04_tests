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
        cls.posts_name = (
            'posts:index',
            'posts:group_list',
            'posts:profile',
            'posts:post_detail',
            'posts:post_create',
            'posts:post_edit',
        )
        cls.kwargs = (
            {'slug': cls.group.slug},
            {'username': cls.user.username},
            {'post_id': cls.post.pk},
        )
        cls.html = (
            'posts/index.html',
            'posts/group_list.html',
            'posts/profile.html',
            'posts/post_detail.html',
            'posts/create_post.html',
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def method_test_context(self, expected, actual, reverse_name):
        response = self.authorized_client.get(reverse_name)
        if actual == 'page_obj':
            actual_post = response.context[actual][0]
        else:
            actual_post = response.context[actual]
        self.assertEqual(actual_post, expected)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""

        templates_pages_names = {
            reverse(self.posts_name[0]): self.html[0],
            reverse(self.posts_name[1], kwargs=self.kwargs[0]): self.html[1],
            reverse(self.posts_name[2], kwargs=self.kwargs[1]): self.html[2],
            reverse(self.posts_name[3], kwargs=self.kwargs[2]): self.html[3],
            reverse(self.posts_name[4]): self.html[4],
            reverse(self.posts_name[5], kwargs=self.kwargs[2]): self.html[4],
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_profile_show_correct_context(self):
        """Шаблоны index, profile, detail
        сформированы с правильным контекстом."""

        pages_addresses_context = {
            reverse(self.posts_name[0]): 'page_obj',
            reverse(self.posts_name[2], kwargs=self.kwargs[1]): 'page_obj',
            reverse(self.posts_name[3], kwargs=self.kwargs[2]): 'post',
        }
        for reverse_name, context in pages_addresses_context.items():
            with self.subTest(reverse_name=reverse_name):
                self.method_test_context(self.post, context, reverse_name)

    def test_page_group_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""

        reverse_name = reverse(self.posts_name[1], kwargs=self.kwargs[0])
        self.method_test_context(self.group, 'group', reverse_name)

    def test_page_post_create_edit_show_correct_context(self):
        """Шаблоны create, edit сформированы с правильным контекстом."""

        pages_addresses = [
            reverse(self.posts_name[4]),
            reverse(self.posts_name[5], kwargs=self.kwargs[2]),
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

        expected_post = self.post
        pages_addresses = [
            reverse(self.posts_name[0]),
            reverse(self.posts_name[1], kwargs=self.kwargs[0]),
            reverse(self.posts_name[2], kwargs=self.kwargs[1]),
        ]
        for reverse_name in pages_addresses:
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertContains(response, expected_post)

    def test_post_not_in_other_group(self):
        """Пост не попал в группу, для которой не был предназначен"""

        post = self.post
        self.group1 = Group.objects.create(
            title='Тестовое описание второе',
            slug='test-slug_2',
            description='Тестовое описание второе',
        )
        revers_name = reverse(
            self.posts_name[1],
            kwargs={'slug': self.group1.slug},
        )
        response = self.authorized_client.get(revers_name)
        self.assertNotContains(response, post)

    def test_pages_paginator(self):
        """Paginator test"""

        for i in range(1, 13):
            Post.objects.create(
                author=self.user,
                text=f'Тестовый пост_{i}',
                group=self.group,
            )
        pages_addresses = [
            reverse(self.posts_name[0]),
            reverse(self.posts_name[1], kwargs=self.kwargs[0]),
            reverse(self.posts_name[2], kwargs=self.kwargs[1]),
        ]
        for reverse_name in pages_addresses:
            page_list = {reverse_name: 10, reverse_name + '?page=2': 3}
            for page, number_post in page_list.items():
                with self.subTest(reverse_name=reverse_name):
                    response = self.client.get(page)
                    self.assertEqual(len(
                        response.context['page_obj']),
                        number_post
                    )
