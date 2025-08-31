"""Minimal urlconf for testing purposes."""

from django.http import HttpResponse
from django.urls import path

from django_windowsauthtoken.views import debug_view


def hello_world(request):
    return HttpResponse("Hello, world!")


urlpatterns = [
    path("debug/", debug_view, name="debug"),
    path("", hello_world, name="home"),
]
