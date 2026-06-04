from __future__ import annotations

from datetime import date

import pytest

from app import create_app
from app.config import TestConfig
from app.database import get_db, init_db, seed_demo_data


@pytest.fixture
def app():
    application = create_app(TestConfig)
    with application.app_context():
        init_db()
        seed_demo_data()
        yield application


@pytest.fixture
def client(app):
    return app.test_client()


def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.get_json()["status"] == "ok"


def test_dashboard_renders(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert b"Salon de Belleza Aurora" in resp.data


def test_dashboard_rejects_invalid_date(client):
    resp = client.get("/?date=not-a-date")
    assert resp.status_code == 400


def test_api_kpis(client):
    resp = client.get("/api/kpis")
    assert resp.status_code == 200
    data = resp.get_json()
    assert "total_appointments" in data
    assert "revenue_cents" in data


def test_api_status_breakdown(client):
    resp = client.get("/api/status-breakdown")
    assert resp.status_code == 200
    assert isinstance(resp.get_json(), dict)


def test_api_revenue_by_service(client):
    resp = client.get("/api/revenue-by-service")
    assert resp.status_code == 200
    assert isinstance(resp.get_json(), list)


def test_api_rejects_invalid_date(client):
    resp = client.get("/api/kpis?date=12-31-2024")
    assert resp.status_code == 400


def test_create_appointment_valid(client):
    today = date.today().isoformat()
    resp = client.post(
        "/appointments",
        data={
            "client_name": "Nuevo Cliente",
            "service_id": "1",
            "appointment_date": today,
        },
        follow_redirects=True,
    )
    assert resp.status_code == 200
    assert b"Appointment created" in resp.data


def test_create_appointment_invalid_name(client):
    today = date.today().isoformat()
    resp = client.post(
        "/appointments",
        data={
            "client_name": "<script>alert(1)</script>",
            "service_id": "1",
            "appointment_date": today,
        },
        follow_redirects=True,
    )
    assert resp.status_code == 200
    assert b"alert(1)" not in resp.data or b"&lt;script&gt;" in resp.data


def test_create_appointment_nonexistent_service(client):
    today = date.today().isoformat()
    resp = client.post(
        "/appointments",
        data={
            "client_name": "Cliente Test",
            "service_id": "9999",
            "appointment_date": today,
        },
        follow_redirects=True,
    )
    assert resp.status_code == 200
    assert b"does not exist" in resp.data


def test_create_appointment_past_date(client):
    resp = client.post(
        "/appointments",
        data={
            "client_name": "Cliente Test",
            "service_id": "1",
            "appointment_date": "2000-01-01",
        },
        follow_redirects=True,
    )
    assert resp.status_code == 200
    assert b"past" in resp.data.lower() or b"appointment_date" in resp.data


def test_security_headers(client):
    resp = client.get("/")
    assert resp.headers["X-Content-Type-Options"] == "nosniff"
    assert resp.headers["X-Frame-Options"] == "DENY"
    assert "Content-Security-Policy" in resp.headers


def test_xss_in_appointment_is_escaped(client):
    today = date.today().isoformat()
    client.post(
        "/appointments",
        data={
            "client_name": "Owasp Tester",
            "service_id": "1",
            "appointment_date": today,
        },
        follow_redirects=True,
    )
    resp = client.get(f"/?date={today}")
    assert resp.status_code == 200
    assert b"<script>alert" not in resp.data


def test_csrf_protection_enabled_in_prod_config():
    from app.config import Config

    assert Config.WTF_CSRF_ENABLED is True
    assert Config.SESSION_COOKIE_HTTPONLY is True
