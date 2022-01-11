from django.shortcuts import render


def page_not_found(request, exception):
    """
    Неизвестная страница вернет 404.
    """
    return render(request, 'core/404.html', {"path": request.path}, status=404)


def csrf_failure(request, reason=''):
    """
    ошибка проверки CSRF, запрос отклонён
    """
    return render(request, 'core/403csrf.html', status=403)


def server_error(request):
    """
    Серверная ошибка.
    """
    return render(request, "core/500.html", status=500)


def page_403_error(request):
    """
    ошибка 403.
    """
    return render(request, 'core/403.html', status=403)
