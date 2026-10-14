"""Tests for the password login and session cookie."""

import pytest
from fastapi.testclient import TestClient

from app import auth
from app.main import app

PASSWORD = "senha-de-teste"


@pytest.fixture
def client(session, monkeypatch) -> TestClient:
    """API client with a password configured and no delay on failed logins."""
    monkeypatch.setattr(auth, "APP_PASSWORD", PASSWORD)
    monkeypatch.setattr(auth, "FAILED_LOGIN_DELAY_SECONDS", 0)
    return TestClient(app)


def test_should_keep_health_check_and_page_shell_public(client):
    assert client.get("/healthz").status_code == 200
    assert client.get("/login").status_code == 200
    assert client.get("/").status_code == 200


def test_should_reject_api_calls_without_session(client):
    response = client.get("/api/status")
    assert response.status_code == 401
    assert "www-authenticate" not in response.headers
    assert client.get("/api/auth/session").json() == {"authenticated": False, "password_required": True}


def test_should_reject_wrong_password(client):
    response = client.post("/api/auth/login", json={"password": "errada"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Senha incorreta"
    assert auth.SESSION_COOKIE not in client.cookies


def test_should_open_session_with_right_password_and_close_on_logout(client):
    login = client.post("/api/auth/login", json={"password": PASSWORD})
    assert login.status_code == 200
    assert "httponly" in login.headers["set-cookie"].lower()
    assert client.get("/api/status").status_code == 200

    client.post("/api/auth/logout")
    assert client.get("/api/status").status_code == 401


def test_should_reject_forged_or_expired_tokens():
    token = auth.create_session_token(now=1_000)
    expires_at = token.split(".")[0]
    assert auth.is_valid_session(token, now=2_000)
    assert not auth.is_valid_session(f"{int(expires_at) + 999}.{token.split('.')[1]}", now=2_000)
    assert not auth.is_valid_session(token, now=int(expires_at) + 1)
    assert not auth.is_valid_session("lixo")


def test_should_not_require_login_without_password(session, monkeypatch):
    monkeypatch.setattr(auth, "APP_PASSWORD", "")
    client = TestClient(app)
    assert client.get("/api/auth/session").json() == {"authenticated": True, "password_required": False}
    assert client.get("/api/status").status_code == 200
