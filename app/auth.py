"""Password login with a signed session cookie.

There is a single user, so a session is just a signed expiry timestamp. The
signing key is derived from ``APP_PASSWORD``: changing the password logs every
browser out. Without a password configured the app is open (local use).
"""

import asyncio
import hashlib
import hmac
import secrets
import time
from typing import Annotated

from fastapi import APIRouter, Cookie, HTTPException, Request, Response, status
from pydantic import BaseModel

from app.config import APP_PASSWORD

SESSION_COOKIE = "toca_session"
SESSION_MAX_AGE_SECONDS = 30 * 24 * 3600
FAILED_LOGIN_DELAY_SECONDS = 1.0

router = APIRouter(prefix="/api/auth")


class LoginIn(BaseModel):
    """Password typed on the login page."""

    password: str


class SessionOut(BaseModel):
    """Whether the browser is logged in and whether a password is required at all."""

    authenticated: bool
    password_required: bool


def require_session(session: Annotated[str | None, Cookie(alias=SESSION_COOKIE)] = None) -> None:
    """FastAPI dependency rejecting requests without a valid session cookie.

    Raises:
        HTTPException: 401 when a password is configured and the session is missing or invalid.
    """
    if not _password_required() or is_valid_session(session):
        return
    raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Faça login para continuar")


@router.get("/session")
def get_session(session: Annotated[str | None, Cookie(alias=SESSION_COOKIE)] = None) -> SessionOut:
    """Report the session state so the UI can decide whether to show the login page."""
    required = _password_required()
    return SessionOut(authenticated=not required or is_valid_session(session), password_required=required)


@router.post("/login")
async def login(credentials: LoginIn, request: Request, response: Response) -> SessionOut:
    """Check the password and start a session.

    Raises:
        HTTPException: 401 when the password is wrong (after a short delay that slows guessing).
    """
    if _password_required() and not secrets.compare_digest(credentials.password.encode(), APP_PASSWORD.encode()):
        await asyncio.sleep(FAILED_LOGIN_DELAY_SECONDS)
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Senha incorreta")
    response.set_cookie(
        SESSION_COOKIE,
        create_session_token(),
        max_age=SESSION_MAX_AGE_SECONDS,
        httponly=True,
        secure=request.url.scheme == "https",
        samesite="lax",
    )
    return SessionOut(authenticated=True, password_required=_password_required())


@router.post("/logout")
def logout(response: Response) -> SessionOut:
    """End the session."""
    response.delete_cookie(SESSION_COOKIE)
    return SessionOut(authenticated=not _password_required(), password_required=_password_required())


def create_session_token(now: float | None = None) -> str:
    """Build a session token: the expiry timestamp and its signature."""
    expires_at = int((now or time.time()) + SESSION_MAX_AGE_SECONDS)
    return f"{expires_at}.{_sign(str(expires_at))}"


def is_valid_session(token: str | None, now: float | None = None) -> bool:
    """Whether the token was signed with the current key and has not expired."""
    if not token or "." not in token:
        return False
    expires_at, signature = token.split(".", 1)
    if not expires_at.isdigit() or not hmac.compare_digest(signature, _sign(expires_at)):
        return False
    return int(expires_at) > (now or time.time())


def _sign(value: str) -> str:
    """HMAC-SHA256 of a value with the key derived from the password."""
    key = hashlib.sha256(f"toca-na-lagoa-session:{APP_PASSWORD}".encode()).digest()
    return hmac.new(key, value.encode(), hashlib.sha256).hexdigest()


def _password_required() -> bool:
    """Whether a password is configured."""
    return bool(APP_PASSWORD)
