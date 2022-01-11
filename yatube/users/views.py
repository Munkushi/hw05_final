from django.views.generic import CreateView
# Функция reverse_lazy позволяет получить URL по параметрам функции path()
from django.urls import reverse_lazy

from .forms import CreationForm

from django.shortcuts import redirect


class SignUp(CreateView):
    form_class = CreationForm
    success_url = reverse_lazy('posts:index')
    template_name = 'users/signup.html'

# def only_user_view(request):
#     if not request.user.is_authenticated:
#         return redirect('/auth/login/')


def authorized_only(func):
    def check_users(request, *arg, **kwargs):
        if request.user.is_authenticated:
            return func(request, *arg, **kwargs)
        return redirect('/auth/login/')
    return check_users
