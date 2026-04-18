import pytest

from template_github_copilot.settings.project import Settings, get_project_settings


# ---------------------------------------------------------------------------
# Project Settings
# ---------------------------------------------------------------------------


def test_get_project_settings_returns_cached_instance():
    """get_project_settings should return the same cached instance."""
    get_project_settings.cache_clear()
    s1 = get_project_settings()
    s2 = get_project_settings()
    assert s1 is s2


def test_settings_defaults(monkeypatch: pytest.MonkeyPatch):
    """Settings should use defaults when no env vars are set."""
    monkeypatch.delenv("PROJECT_NAME", raising=False)
    monkeypatch.delenv("PROJECT_LOG_LEVEL", raising=False)
    settings = Settings(_env_file=None)  # type: ignore[call-arg]  # ty: ignore[unknown-argument]
    assert settings.project_name == "default-project"
    assert settings.project_log_level == "INFO"


def test_settings_from_env(monkeypatch: pytest.MonkeyPatch):
    """Settings should pick up values from environment variables."""
    monkeypatch.setenv("PROJECT_NAME", "my-project")
    monkeypatch.setenv("PROJECT_LOG_LEVEL", "DEBUG")
    settings = Settings(_env_file=None)  # type: ignore[call-arg]  # ty: ignore[unknown-argument]
    assert settings.project_name == "my-project"
    assert settings.project_log_level == "DEBUG"
