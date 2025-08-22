"""View-классы приложения pages."""
from django.shortcuts import render
from django.views.generic import TemplateView


class AboutView(TemplateView):
    """Страничка "О проекте"."""

    template_name = 'pages/about.html'


class RulesView(TemplateView):
    """Страничка "Правила"."""

    template_name = 'pages/rules.html'


def page_not_found(request, exception):
    return render(request, 'pages/404.html', status=404)


def server_error(request):
    return render(request, 'pages/500.html', status=500)


def csrf_failure(request, reason='', **kwargs):
    return render(request, 'pages/403csrf.html', status=403)
