"""
URL configuration for sample_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.http import HttpResponse
from django.template import Context, Template
from django.urls import path


def windowsauthtoken_debug(request):
    """
    A simple view to display the WindowsAuthToken debug information.

    A template string is used here for simplicity.
    It's rendered directly without needing a separate HTML file.
    """
    template_string = """
    <h1>WindowsAuthToken Debug Information</h1>
    <h2>User Information:</h2>
    <p>Username: {{ request.user.username }}</p>
    <p>Is Authenticated: {{ request.user.is_authenticated }}</p>
    <p>Is Anonymous: {{ request.user.is_anonymous }}</p>

    <h2>Request headers:</h2>
    <p{% for k, v in request.headers.items %}{{ k }}: {{ v }}<br/>{% endfor %}</p>

    <h2>Request META Information:</h2>
    <p>{% for k, v in request.META.items %}{{ k }}: {{ v }}<br/>{% endfor %}</p>
    """
    return HttpResponse(Template(template_string).render(Context({"request": request})), content_type="text/html")


urlpatterns = [
    path("admin/", admin.site.urls),
    path("windowsauthtoken-debug", windowsauthtoken_debug),
]
