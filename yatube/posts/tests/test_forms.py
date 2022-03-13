from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post

User = get_user_model()


class PostCreatFormTests(TestCase):
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
        cls.reverse_name = (
            reverse('posts:post_create'),
            reverse(
                'posts:post_edit',
                kwargs={'post_id': cls.post.pk},
            )
        )

    def setUp(self):
        self.authorized_client = Client()
        self.user = self.user
        self.authorized_client.force_login(self.user)

    def test_post_create(self):
        """Валидная форма создает пост."""

        posts_count = Post.objects.count()
        form_data = {
            'group': self.group.pk,
            'text': 'Тестовый пост_1',
        }
        response = self.authorized_client.post(
            self.reverse_name[0],
            data=form_data,
            follow=True,
        )
        self.assertEqual(Post.objects.count(), (posts_count + 1))
        post_create = Post.objects.filter(
            group=self.group.pk,
            text='Тестовый пост_1',
        )
        self.assertTrue(post_create.exists())
        self.assertEqual(response.status_code, 200)
        post = Post.objects.get(
            group=self.group.pk,
            text='Тестовый пост_1',
        )
        self.assertEqual(post.author, self.post.author)
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(post.group.pk, form_data['group'])

    def test_post_edit(self):
        """Валидная форма редактирует пост"""

        post_count = Post.objects.count()
        form_data = {
            'group': self.group.pk,
            'text': 'редактируемый пост',
        }
        self.authorized_client.post(
            self.reverse_name[1],
            date=form_data,
            follow=True,
        )
        self.assertEqual(Post.objects.count(), post_count)
        post_is_edit = Post.objects.filter(pk=self.post.pk)
        self.assertTrue(post_is_edit.exists())
        post = Post.objects.get(pk=self.post.pk)
        self.assertEqual(post.author, self.post.author)
        self.assertEqual(post.group.pk, form_data['group'])
