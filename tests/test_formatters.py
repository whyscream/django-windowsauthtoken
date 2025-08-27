import pytest

from django_windowsauthtoken.formatters import (
    FormattingError,
    format_email_like,
    format_username_domain_user,
    format_username_only,
)


def test_format_username_domain_user():
    assert format_username_domain_user("testuser", "TESTDOMAIN") == r"TESTDOMAIN\testuser"


def test_format_username_domain_user_empty_domain():
    with pytest.raises(FormattingError):
        format_username_domain_user("testuser", "")


def test_format_username_domain_user_empty_user():
    with pytest.raises(FormattingError):
        format_username_domain_user("", "TESTDOMAIN")


def test_format_username_domain_user_both_empty():
    with pytest.raises(FormattingError):
        format_username_domain_user("", "")


def testformat_username_only():
    assert format_username_only("testuser", "TESTDOMAIN") == "testuser"


def test_format_username_only_empty_user():
    with pytest.raises(FormattingError):
        format_username_only("", "TESTDOMAIN")


def test_format_username_only_empty_domain():
    assert format_username_only("testuser", "") == "testuser"


def test_format_username_only_both_empty():
    with pytest.raises(FormattingError):
        format_username_only("", "")


def test_format_email_like():
    assert format_email_like("testuser", "TESTDOMAIN") == "testuser@TESTDOMAIN"


def test_format_email_like_empty_user():
    with pytest.raises(FormattingError):
        format_email_like("", "TESTDOMAIN")


def test_format_email_like_empty_domain():
    with pytest.raises(FormattingError):
        format_email_like("testuser", "")


def test_format_email_like_both_empty():
    with pytest.raises(FormattingError):
        format_email_like("", "")
