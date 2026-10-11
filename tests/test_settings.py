"""The tests must use the values from conftest.py, never the developer's .env file."""
from app.core.config import Settings, settings
from app.db.session import engine

def test_every_setting_is_pinned_by_the_tests(test_settings):
    # A new setting without a test value could be read from .env
    assert set(Settings.model_fields) == set(test_settings)

def test_settings_come_from_test_environment(test_settings):
    for name, expected in test_settings.items():
        assert str(getattr(settings, name)).lower() == expected.lower(), name

def test_app_engine_is_in_memory_sqlite():
    assert engine.url.get_backend_name() == "sqlite"
    assert engine.url.database in (None, "", ":memory:")
