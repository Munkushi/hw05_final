from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post

User = get_user_model()


def index(request):
    """
    Главная страница.
    """
    posts = Post.objects.select_related("author", "group").all()
    paginator = Paginator(posts, settings.PAGINATOR_NUM)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    context = {
        "page_obj": page_obj,
    }
    return render(request, "posts/index.html", context)


def group_posts(request, slug):
    """
    Группы.
    """
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    paginator = Paginator(posts, settings.PAGINATOR_NUM)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    context = {
        "page_obj": page_obj,
        "group": group,
    }
    return render(request, "posts/group_list.html", context)


def profile(request, username):
    """
    Профиль пользователя.
    """
    author = get_object_or_404(User, username=username)
    post = author.posts.all()
    number_of_posts = author.posts.count()
    paginator = Paginator(post, settings.PAGINATOR_NUM)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    following = Follow.objects.filter(
        user__username=request.user, author=author
    )
    context = {
        "page_obj": page_obj,
        "author": author,
        "number_of_posts": number_of_posts,
        "following": following,
    }
    return render(request, "posts/profile.html", context)


def post_detail(request, post_id):
    """
    Страница с деталями поста.
    """

    post = get_object_or_404(Post, pk=post_id)
    comments = post.comments.all()
    post_count = post.author.posts.count()
    form = CommentForm(request.POST or None)
    context = {
        "post": post,
        "post_count": post_count,
        "comments": comments,
        "form": form,
    }
    return render(request, "posts/post_detail.html", context)


@login_required
def post_create(request):
    """
    Страница создания поста.
    """

    if request.method == "POST":
        form = PostForm(request.POST, files=request.FILES or None)
        if form.is_valid():
            form.instance.author = request.user
            form.save()
            return redirect("posts:profile", request.user)
        return render(
            request,
            "posts/create_post.html",
            {
                "form": form,
                "is_edit": False,
            },
        )
    form = PostForm()
    return render(
        request,
        "posts/create_post.html",
        {
            "form": form,
            "is_edit": False,
        },
    )


@login_required
def post_edit(request, post_id):
    """
    Страница редактирования поста.
    """
    post = get_object_or_404(Post, pk=post_id)
    if post.author != request.user:
        return redirect('posts:post_detail', post_id=post_id)

    form = PostForm(
        request.POST or None, files=request.FILES or None, instance=post
    )
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id=post_id)
    context = {
        'post': post,
        'form': form,
        'is_edit': True,
    }
    return render(request, 'posts/create_post.html', context)


@login_required
def add_comment(request, post_id):
    """
    Комментарии.
    """
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    """
    Вью подписки.
    """

    posts = Post.objects.filter(author__following__user=request.user)
    paginator = Paginator(posts, settings.PAGINATOR_NUM)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    context = {"page_obj": page_obj}
    return render(request, "posts/follow.html", context)


@login_required
def profile_follow(request, username):
    """
    Подписка на других авторов.
    """

    author = get_object_or_404(User, username=username)
    if author != request.user:
        Follow.objects.get_or_create(author=author, user=request.user)
    return redirect("posts:profile", request.user)


@login_required
def profile_unfollow(request, username):
    """
    Дизлайк/отписка от других авторов.
    """

    author = get_object_or_404(User, username=username)
    follow_obj = get_object_or_404(Follow, author=author, user=request.user)
    follow_obj.delete()
    return redirect("posts:profile", request.user)
