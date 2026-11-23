import runpy
from pathlib import Path

import pytest

SETTINGS_FILE = Path(__file__).resolve().parents[1] / "config" / "settings.py"
DEFAULT_LANGUAGES = ("Python", "TypeScript", "JavaScript")


def load_languages() -> tuple[str, ...]:
    languages: tuple[str, ...] = runpy.run_path(str(SETTINGS_FILE))["RANKINGS_LANGUAGES"]
    return languages


def test_rankings_languages_default_when_unset(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("RANKINGS_LANGUAGES", raising=False)

    assert load_languages() == DEFAULT_LANGUAGES


@pytest.mark.parametrize("value", ["", "   ", " , ,"])
def test_rankings_languages_default_when_blank(monkeypatch: pytest.MonkeyPatch, value: str) -> None:
    monkeypatch.setenv("RANKINGS_LANGUAGES", value)

    assert load_languages() == DEFAULT_LANGUAGES


def test_rankings_languages_parses_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("RANKINGS_LANGUAGES", " Go, rust,,GO ")

    assert load_languages() == ("Go", "rust")


def test_rankings_languages_keeps_names_with_spaces(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("RANKINGS_LANGUAGES", "Jupyter Notebook,Python")

    assert load_languages() == ("Jupyter Notebook", "Python")
