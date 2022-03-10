from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from yatube.settings import NUMBER_OF_POSTS

from .forms import PostForm
from .models import Group, Post
from .utils import paginator_method

User = get_user_model()


def index(request):
    post_list = Post.objects.all()
    page_obj = paginator_method(request, post_list, NUMBER_OF_POSTS)
    template = 'posts/index.html'
    context = {
        'page_obj': page_obj,
    }
    return render(request, template, context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    template = 'posts/group_list.html'
    posts = group.posts.all()
    page_obj = paginator_method(request, posts, NUMBER_OF_POSTS)
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, template, context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts = author.posts.all()
    page_obj = paginator_method(request, posts, NUMBER_OF_POSTS)
    posts_count = posts.count()
    context = {
        'author': author,
        'page_obj': page_obj,
        'posts_count': posts_count,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    author = post.author
    post_count = author.posts.all().count()
    context = {
        'post': post,                  # Имена 'requrst_name' и 'post_name'
        'post_count': post_count,      # для ссылки на редоктирование поста
        'request_name': request.user,  # Если 'requret_name' == 'post_name'
        'post_author': author,           # то пользователь видит ссылку
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    form = PostForm(request.POST or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:profile', username=request.user)
    form = PostForm()
    context = {'form': form}
    return render(request, 'posts/create_post.html', context)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if request.user.username != post.author.username:
        return redirect('posts:post_detail', post_id=post_id)
    form = PostForm(request.POST, instance=post)
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id=post_id)
    form = PostForm(instance=post)
    context = {'form': form, 'is_edit': True}
    return render(request, 'posts/create_post.html', context)
