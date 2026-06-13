import pytest
from pydantic import ValidationError

from app.core.config import Settings


def test_settings_require_env_values(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("SECRET_KEY", raising=False)
    monkeypatch.delenv("JWT_SECRET_KEY", raising=False)

    with pytest.raises(ValidationError):
        Settings(_env_file=None)


def test_settings_reject_placeholder_values():
    with pytest.raises(ValidationError):
        Settings(
            DATABASE_URL=(
                "postgresql://user:password@host.neon.tech/"
                "dbname?sslmode=require"
            ),
            SECRET_KEY=(
                "replace-with-a-long-random-secret-at-least-32-characters"
            ),
            _env_file=None,
        )
