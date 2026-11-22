from django.conf import settings


def test_project_settings_load() -> None:
    assert "rest_framework" in settings.INSTALLED_APPS
    assert settings.USE_TZ is True
    assert settings.TIME_ZONE == "UTC"
