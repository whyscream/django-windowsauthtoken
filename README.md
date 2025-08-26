# Windows Authentication token handling for Django

When IIS on Windows is used as a webserver frontend for Django, authentication can be handled by the webserver using Windows Authentication. Microsoft recommends using the HttpPlatformHandler method to integrate Python webapps with IIS. Unlike when using the older and unmaintained `wfastcgi`, the HttpPlatformHandler doesn't set the `REMOTE_USER` variable after authentication. Instead, the authenticated user's token is available as a header named `X-IIS-WindowsAuthToken`.

This package provides a Django middleware that extracts the token from the header, requests the actual username from Windows, and sets the `REMOTE_USER` variable accordingly. This allows you to use Django's built-in authentication mechanisms seamlessly.

## Installation

You can install the package using pip:

```bash
pip install django-windowsauthtoken
```

After installation, add the middleware to your Django settings:

```python
MIDDLEWARE = [
    ...,
    "django_windowsauthtoken.middleware.WindowsAuthTokenMiddleware",
    # Ensure this is placed before any authentication middleware
    # You'll likely want to use Django's built-in RemoteUserMiddleware
    "django.contrib.auth.middleware.RemoteUserMiddleware",
    ...
]
```

Now configure IIS to integrate with your Django application using the HttpPlatformHandler, and ensure that Windows Authentication is enabled for your site.

## Usage

Once the middleware is added, it will automatically handle the extraction of the Windows Authentication token from the `X-IIS-WindowsAuthToken` header and set the `REMOTE_USER` variable. You can then use Django's authentication system as usual.
