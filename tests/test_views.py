import pytest


@pytest.mark.django_db
def test_debug_view_authenticated_success(settings, mocker, client):
    settings.DEBUG = True

    mocker.patch(
        "django_windowsauthtoken.middleware.WindowsAuthTokenMiddleware.retrieve_auth_user_details",
        return_value=("testuser", "TESTDOMAIN"),
    )

    response = client.get("/debug/", headers={"X-Iis-WindowsAuthToken": "123"})
    assert response.status_code == 200

    data = response.json()
    assert data["META___HTTP_X_IIS_WINDOWSAUTHTOKEN"] == "123"
    assert data["META___REMOTE_USER"] == r"TESTDOMAIN\testuser"
    assert data["META___HTTP_REMOTE_USER"] == r"TESTDOMAIN\testuser"
    assert data["META___WINDOWSAUTHTOKEN_USER"] == "testuser"
    assert data["META___WINDOWSAUTHTOKEN_DOMAIN"] == "TESTDOMAIN"
    assert data["user.is_authenticated"] is True
    assert data["user.is_anonymous"] is False
    assert data["user.username"] == r"TESTDOMAIN\testuser"
    assert "request" in data
    assert "META" in data


def test_debug_view_unauthenticated_success(settings, client):
    settings.DEBUG = True

    response = client.get("/debug/")
    assert response.status_code == 200

    data = response.json()
    assert data["META___HTTP_X_IIS_WINDOWSAUTHTOKEN"] == "N/A"
    assert data["META___REMOTE_USER"] == "N/A"
    assert data["META___HTTP_REMOTE_USER"] == "N/A"
    assert data["META___WINDOWSAUTHTOKEN_USER"] == "N/A"
    assert data["META___WINDOWSAUTHTOKEN_DOMAIN"] == "N/A"
    assert data["user.is_authenticated"] is False
    assert data["user.is_anonymous"] is True
    assert data["user.username"] == "N/A"
    assert "request" in data
    assert "META" in data


def test_debug_view_not_debug(client, settings):
    settings.DEBUG = False

    response = client.get("/debug/")
    assert response.status_code == 200

    data = response.json()
    assert data == {"error": "This view is only available in DEBUG mode."}
