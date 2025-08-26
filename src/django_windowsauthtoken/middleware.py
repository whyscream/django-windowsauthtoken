import logging
import os

from django.core.exceptions import ImproperlyConfigured

logger = logging.getLogger("windowsauthtoken")

_IGNORE_PLATFORM_ERRORS = os.getenv("WINDOWSAUTHTOKEN_IGNORE_PLATFORM_ERRORS", "false") == "true"

try:
    import pywintypes, win32api, win32security
except ImportError:
    if _IGNORE_PLATFORM_ERRORS:
        logger.info("pywin32 is not installed, but platform errors are being ignored.")
        pywintypes = None
        win32api = None
        win32security = None
    else:
        raise ImproperlyConfigured("pywin32 is required for Windows Authentication Token middleware.")


class WindowsAuthTokenMiddleware:
    """
    Middleware to handle Windows Authentication Tokens and convert them to a `REMOTE_USER` environment variable.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        auth_token = request.headers.get("X-IIS-WindowsAuthToken", "")
        if auth_token:
            try:
                username, domain = self.retrieve_username(auth_token)
            except ValueError:
                logger.warning("Could not retrieve username from auth token.")
                username = None
                domain = None

            if username and domain:
                # Set the REMOTE_USER environment variable
                domain_user = rf"{domain}\{username}"
                request.META['REMOTE_USER'] = domain_user
                logger.debug(f"Set REMOTE_USER to {domain_user}")

        return self.get_response(request)

    @staticmethod
    def retrieve_auth_user_details(auth_token: str) -> tuple[str, str]:
        """
        Retrieve the user details for the Windows Authentication Token.

        Uses pywin32 to access the hosts' API to extract the username and domain for the token.

        Args:
            auth_token (str): The Windows Authentication Token.
        Returns:
            tuple[str, str]: A tuple containing the username and domain.
        Raises:
            ValueError: If the token is invalid or cannot be processed.
        """
        if win32security is None:
            raise ValueError("pywin32 is not available to process the token.")

        try:
            token_handle = int(token, 16)
        except ValueError:
            raise ValueError("Invalid token format.")

        try:
            # See https://learn.microsoft.com/en-us/windows/win32/api/winnt/ne-winnt-token_information_class
            token_information_class = 1
            security_id, _ = win32security.GetTokenInformation(token_handle, token_information_class)
            logger.debug(f"Retrieved SID for auth token: {auth_token=} {token_handle=} {security_id=}")
        except pywintypes.error as err:
            raise ValueError(f"Token handle is invalid, can't retrieve SID: {err}")
            return _invalid
        finally:
            win32api.CloseHandle(token_handle)

        try:
            user, domain, account_type = win32security.LookupAccountSid(None, security_id)
            logger.debug(f"Retrieved account details for SID: {security_id=} {user=} {domain=} {account_type=}")
        except TypeError as err:
            # Not really sure what other exceptions we should catch
            raise ValueError(f"Can't retrieve account details for SID: {err}")

        return user, domain
