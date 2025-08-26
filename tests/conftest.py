import os

from django.conf import settings


def pytest_configure():
    # Make sure that we can run all tests even on non-Windows platforms
    os.environ.setdefault("WINDOWSAUTHTOKEN_IGNORE_PLATFORM_ERRORS", "true")
    # Set up Django settings for the tests
    settings.configure(MIDDLEWARE=[
        "django.middleware.security.SecurityMiddleware",
        "django.contrib.sessions.middleware.SessionMiddleware",
        "django.middleware.common.CommonMiddleware",
        "django.middleware.csrf.CsrfViewMiddleware",
        # Add the WindowsAuthTokenMiddleware here
        "django_windowsauthtoken.middleware.WindowsAuthTokenMiddleware",
        "django.contrib.auth.middleware.AuthenticationMiddleware",
        "django.contrib.messages.middleware.MessageMiddleware",
        "django.middleware.clickjacking.XFrameOptionsMiddleware",
    ])
