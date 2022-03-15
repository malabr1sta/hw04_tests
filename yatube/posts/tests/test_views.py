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
        cls.index_page = (
            'posts:index',
            None,
            'posts/index.html',
        )
        cls.group_page = (
            'posts:group_list',
            {'slug': cls.group.slug},
            'posts/group_list.html',
        )
        cls.profile_page = (
            'posts:profile',
            {'username': cls.user.username},
            'posts/profile.html',
        )
        cls.detail_page = (
            'posts:post_detail',
            {'post_id': cls.post.pk},
            'posts/post_detail.html',
        )
        cls.create_page = (
            'posts:post_create',
            None,
            'posts/create_post.html',
        )
        cls.edit_page = (
            'posts:post_edit',
            {'post_id': cls.post.pk},
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

        pages = (
            self.index_page,
            self.group_page,
            self.profile_page,
            self.detail_page,
            self.create_page,
            self.edit_page,
        )
        templates_pages = {reverse(i[0], kwargs=i[1]): i[2] for i in pages}
        for reverse_name, template in templates_pages.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_profile_show_correct_context(self):
        """Шаблоны index, profile, detail
        сформированы с правильным контекстом."""

        pages_addresses_context = {
            reverse(self.index_page[0]): 'page_obj',
            reverse(
                self.profile_page[0],
                kwargs=self.profile_page[1]
            ): 'page_obj',
            reverse(self.detail_page[0], kwargs=self.detail_page[1]): 'post',
        }
        for reverse_name, context in pages_addresses_context.items():
            with self.subTest(reverse_name=reverse_name):
                self.method_test_context(self.post, context, reverse_name)

    def test_page_group_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""

        reverse_name = reverse(self.group_page[0], kwargs=self.group_page[1])
        self.method_test_context(self.group, 'group', reverse_name)

    def test_page_post_create_edit_show_correct_context(self):
        """Шаблоны create, edit сформированы с правильным контекстом."""

        pages_addresses = [
            reverse(self.create_page[0]),
            reverse(self.edit_page[0], kwargs=self.edit_page[1]),
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
        pages = (self.index_page, self.group_page, self.profile_page,)
        pages_addresses = [reverse(i[0], kwargs=i[1]) for i in pages]
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
            self.group_page[0],
            kwargs={'slug': self.group1.slug},
        )
        response = self.authorized_client.get(revers_name)
        self.assertNotContains(response, post)

    def test_pages_paginator(self):
        """Paginator test"""

        posts = []
        for i in range(1, 13):
            posts.append(Post(
                author=self.user,
                text=f'Тестовый пост_{i}',
                group=self.group,
            ))
        Post.objects.bulk_create(posts, 13)
        pages = (self.index_page, self.group_page, self.profile_page)
        pages_addresses = [reverse(i[0], kwargs=i[1]) for i in pages]
        for reverse_name in pages_addresses:
            page_list = {reverse_name: 10, reverse_name + '?page=2': 3}
            for page, number_post in page_list.items():
                with self.subTest(reverse_name=reverse_name):
                    response = self.client.get(page)
                    self.assertEqual(len(
                        response.context['page_obj']),
                        number_post
                    )
