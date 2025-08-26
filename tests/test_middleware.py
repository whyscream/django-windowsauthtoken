from collections import namedtuple

import pytest
from django.core.exceptions import ImproperlyConfigured

from django_windowsauthtoken.middleware import WindowsAuthTokenMiddleware


@pytest.fixture()
def mock_pywin32(mocker):
    """Fixture to mock pywin32 components used in the middleware."""
    mock_win32security = mocker.patch("django_windowsauthtoken.middleware.win32security")
    mock_win32api = mocker.patch("django_windowsauthtoken.middleware.win32api")
    mock_pywintypes = mocker.patch("django_windowsauthtoken.middleware.pywintypes")
    mock_pywintypes.error = Pywin32MockException

    # Return a namedtuple for easier access to the mocks
    pywin32_mock = namedtuple("pywin32_mock", ["win32security", "win32api", "pywintypes"])
    return pywin32_mock(mock_win32security, mock_win32api, mock_pywintypes)


def test_middleware_sets_remote_user(mocker, rf):
    mocker.patch(
        "django_windowsauthtoken.middleware.WindowsAuthTokenMiddleware.retrieve_auth_user_details",
        return_value=("testuser", "TESTDOMAIN"),
    )

    mock_get_response = mocker.Mock()
    middleware = WindowsAuthTokenMiddleware(mock_get_response)

    request = rf.get("/")
    request.headers = {"X-IIS-WindowsAuthToken": "valid_token"}
    request.META = {}

    response = middleware(request)

    assert response == mock_get_response.return_value
    assert request.META["REMOTE_USER"] == r"TESTDOMAIN\testuser"
    mock_get_response.assert_called_once_with(request)


def test_middleware_no_token(rf, mocker):
    mock_get_response = mocker.Mock()
    middleware = WindowsAuthTokenMiddleware(mock_get_response)

    request = rf.get("/")
    request.headers = {}
    request.META = {}

    response = middleware(request)

    assert response == mock_get_response.return_value
    assert "REMOTE_USER" not in request.META
    mock_get_response.assert_called_once_with(request)


def test_middleware_invalid_token(mocker, rf):
    mocker.patch(
        "django_windowsauthtoken.middleware.WindowsAuthTokenMiddleware.retrieve_auth_user_details",
        side_effect=ValueError("Invalid token"),
    )

    mock_get_response = mocker.Mock()
    middleware = WindowsAuthTokenMiddleware(mock_get_response)

    request = rf.get("/")
    request.headers = {"X-IIS-WindowsAuthToken": "invalid_token"}
    request.META = {}

    response = middleware(request)

    assert response == mock_get_response.return_value
    assert "REMOTE_USER" not in request.META
    mock_get_response.assert_called_once_with(request)


def test_retrieve_auth_user_details_invalid_token():
    with pytest.raises(ValueError) as excinfo:
        WindowsAuthTokenMiddleware.retrieve_auth_user_details("invalid_token")
    assert "Invalid token format" in str(excinfo.value)


class Pywin32MockException(Exception):
    """Mock exception to simulate pywin32 errors."""

    pass


def test_retrieve_auth_user_details_no_token_information(mock_pywin32):
    mock_pywin32.win32security.GetTokenInformation.side_effect = Pywin32MockException("No token information")

    with pytest.raises(ValueError) as excinfo:
        WindowsAuthTokenMiddleware.retrieve_auth_user_details("123")
    assert "Can't retrieve Security ID for token: No token information" in str(excinfo.value)

    mock_pywin32.win32security.GetTokenInformation.assert_called_once_with(291, 1)


def test_retrieve_auth_user_details_no_account(mock_pywin32):
    # GetTokenInformation returns a SID object and some integer value
    mock_pywin32.win32security.GetTokenInformation.return_value = ("mocked_sid", 0)
    mock_pywin32.win32security.LookupAccountSid.side_effect = Pywin32MockException("No account found")

    with pytest.raises(ValueError) as excinfo:
        WindowsAuthTokenMiddleware.retrieve_auth_user_details("123")
    assert "Can't retrieve account details for SID: No account found" in str(excinfo.value)

    mock_pywin32.win32security.GetTokenInformation.assert_called_once_with(291, 1)
    mock_pywin32.win32security.LookupAccountSid.assert_called_once_with(None, "mocked_sid")


def test_retrieve_auth_user_details_invalid_sid_object(mock_pywin32):
    # GetTokenInformation returns a SID object and some integer value
    mock_pywin32.win32security.GetTokenInformation.return_value = ("mocked_sid", 0)
    mock_pywin32.win32security.LookupAccountSid.side_effect = TypeError("Invalid SID object")

    with pytest.raises(ValueError) as excinfo:
        WindowsAuthTokenMiddleware.retrieve_auth_user_details("123")
    assert "Can't retrieve account details for SID: Invalid SID object" in str(excinfo.value)

    mock_pywin32.win32security.GetTokenInformation.assert_called_once_with(291, 1)
    mock_pywin32.win32security.LookupAccountSid.assert_called_once_with(None, "mocked_sid")


def test_retrieve_auth_user_details_success(mock_pywin32):
    # GetTokenInformation returns a SID object and some integer value
    mock_pywin32.win32security.GetTokenInformation.return_value = ("mocked_sid", 0)
    # LookupAccountSid returns a tuple of (username, domain, account_type)
    mock_pywin32.win32security.LookupAccountSid.return_value = (
        "testuser",
        "TESTDOMAIN",
        1,
    )

    username, domain = WindowsAuthTokenMiddleware.retrieve_auth_user_details("123")

    assert username == "testuser"
    assert domain == "TESTDOMAIN"

    mock_pywin32.win32security.GetTokenInformation.assert_called_once_with(291, 1)
    mock_pywin32.win32security.LookupAccountSid.assert_called_once_with(None, "mocked_sid")
    mock_pywin32.win32api.CloseHandle.assert_called_once()


def test_configure_pywin32_error_handling(monkeypatch):
    monkeypatch.setenv("WINDOWSAUTHTOKEN_IGNORE_PYWIN32_ERRORS", "false")
    # Reload the middleware module to apply the environment variable change
    import importlib

    from django_windowsauthtoken import middleware

    with pytest.raises(ImproperlyConfigured) as excinfo:
        importlib.reload(middleware)
    assert "pywin32 is required for Windows Authentication Token middleware." in str(excinfo.value)
