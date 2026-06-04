from __future__ import annotations

import os
import secrets


class Config:
    SECRET_KEY = os.environ.get("FLASK_SECRET_KEY") or secrets.token_urlsafe(48)

    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = os.environ.get("FLASK_ENV") == "production"

    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600

    MAX_CONTENT_LENGTH = 256 * 1024

    DATABASE_PATH = os.environ.get("SALON_DB_PATH", "salon.db")

    PERMANENT_SESSION_LIFETIME = 1800


class TestConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False
    DATABASE_PATH = ":memory:"
    SECRET_KEY = secrets.token_urlsafe(32)
