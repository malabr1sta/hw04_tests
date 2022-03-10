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

    def setUp(self):
        self.authorized_client = Client()
        self.user = PostCreatFormTests.user
        self.authorized_client.force_login(self.user)

    def test_post_create(self):
        """Валидная форма создает пост."""

        posts_count = Post.objects.count()
        form_data = {
            'group': PostCreatFormTests.group.pk,
            'text': 'Тестовый пост',
        }
        self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True,
        )
        self.assertEqual(Post.objects.count(), (posts_count + 1))
        post_create = Post.objects.filter(
            group=PostCreatFormTests.group.pk,
            text='Тестовый пост',
        )
        self.assertTrue(post_create.exists())

    def test_post_edit(self):
        """Валидная форма редактирует пост"""

        post_count = Post.objects.count()
        form_data = {
            'group': PostCreatFormTests.group.pk,
            'text': 'редактируемый пост',
        }
        reverse_name_edit = reverse(
            'posts:post_edit',
            kwargs={'post_id': PostCreatFormTests.post.pk},
        )
        self.authorized_client.post(
            reverse_name_edit,
            date=form_data,
            follow=True,
        )
        self.assertEqual(Post.objects.count(), post_count)
        post_is_edit = Post.objects.filter(pk=PostCreatFormTests.post.pk)
        self.assertTrue(post_is_edit.exists())
