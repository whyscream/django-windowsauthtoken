from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.http import require_GET


@require_GET
def debug_view(request):
    """
    A simple debug view that returns the current user's username and domain.
    """
    if not settings.DEBUG:
        return JsonResponse({"error": "This view is only available in DEBUG mode."})

    return JsonResponse(
        {
            # Include relevant META information for easy debugging
            "META___HTTP_X_IIS_WINDOWSAUTHTOKEN": request.META.get("HTTP_X_IIS_WINDOWSAUTHTOKEN", "N/A"),
            "META___REMOTE_USER": request.META.get("REMOTE_USER", "N/A"),
            "META___HTTP_REMOTE_USER": request.META.get("HTTP_REMOTE_USER", "N/A"),
            "META___WINDOWSAUTHTOKEN_USER": request.META.get("WINDOWSAUTHTOKEN_USER", "N/A"),
            "META___WINDOWSAUTHTOKEN_DOMAIN": request.META.get("WINDOWSAUTHTOKEN_DOMAIN", "N/A"),
            # State of the user object
            "user.is_authenticated": request.user.is_authenticated,
            "user.is_anonymous": request.user.is_anonymous,
            "user.username": request.user.username if request.user.is_authenticated else "N/A",
            # Full request representation for deeper debugging if needed, mainly ASGI/WSGI differences
            "request": str(request),
            # Full META dump for deeper debugging if needed
            "META": {k: str(v) for k, v in request.META.items()},
        }
    )
