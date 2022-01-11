from django import forms

from .models import Comment, Post


class PostForm(forms.ModelForm):
    """
    Форма поста.
    """

    class Meta:
        model = Post
        fields = ('group', 'text', 'image')


class CommentForm(forms.ModelForm):
    """
    Форма комментария.
    """

    class Meta:
        model = Comment
        fields = ('text',)
