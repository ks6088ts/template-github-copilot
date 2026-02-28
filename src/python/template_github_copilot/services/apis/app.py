"""FastAPI application with OAuth GitHub App authentication and Copilot chat.

This module provides:
- GitHub OAuth login/callback flow
- Session-based token storage (in-memory, signed cookies)
- ``/api/chat`` endpoint that proxies user messages to the Copilot SDK
- Plain HTML frontend served at ``/``
"""

from __future__ import annotations

import hashlib
import hmac
import logging
import secrets
import time
from pathlib import Path
from typing import Any

import httpx
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from template_github_copilot.core import (
    create_copilot_client,
    create_event_handler,
    create_message_options,
    create_session_config,
)
from template_github_copilot.services.reports import ReportOutput, run_parallel_chat
from template_github_copilot.settings import OAuthSettings, get_oauth_settings

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------


class ChatRequest(BaseModel):
    """Incoming chat request from the frontend."""

    message: str = Field(
        ..., min_length=1, description="User message to send to Copilot."
    )


class ChatResponse(BaseModel):
    """Response returned to the frontend."""

    reply: str = Field(..., description="Copilot's response text.")


class ReportRequest(BaseModel):
    """Incoming report request."""

    queries: list[str] = Field(
        ..., min_length=1, description="List of user queries to run in parallel."
    )
    system_prompt: str = Field(
        ..., min_length=1, description="System prompt for Copilot sessions."
    )


class UserInfo(BaseModel):
    """Minimal GitHub user information."""

    login: str
    avatar_url: str | None = None


# ---------------------------------------------------------------------------
# Lightweight signed-cookie session helpers
# ---------------------------------------------------------------------------

# In-memory session store: session_id -> dict
_sessions: dict[str, dict[str, Any]] = {}


def _sign(value: str, secret: str) -> str:
    """Return ``value.signature`` using HMAC-SHA256."""
    sig = hmac.new(secret.encode(), value.encode(), hashlib.sha256).hexdigest()
    return f"{value}.{sig}"


def _verify(signed: str, secret: str) -> str | None:
    """Verify a signed value and return the original, or ``None``."""
    parts = signed.rsplit(".", 1)
    if len(parts) != 2:
        return None
    value, sig = parts
    expected = hmac.new(secret.encode(), value.encode(), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(sig, expected):
        return None
    return value


def _get_session(request: Request, secret: str) -> dict[str, Any]:
    """Return the session dict for the current request, or empty dict."""
    cookie = request.cookies.get("session_id")
    if cookie is None:
        return {}
    sid = _verify(cookie, secret)
    if sid is None:
        return {}
    return _sessions.get(sid, {})


# ---------------------------------------------------------------------------
# Application factory
# ---------------------------------------------------------------------------

GITHUB_AUTHORIZE_URL = "https://github.com/login/oauth/authorize"
GITHUB_TOKEN_URL = "https://github.com/login/oauth/access_token"
GITHUB_USER_URL = "https://api.github.com/user"


def create_app(settings: OAuthSettings | None = None) -> FastAPI:
    """Create and return the configured FastAPI application.

    Args:
        settings: Optional ``OAuthSettings``; falls back to env/dotenv when
            ``None``.

    Returns:
        A fully-configured ``FastAPI`` instance.
    """
    if settings is None:
        settings = get_oauth_settings()

    app = FastAPI(title="Copilot Chat (OAuth GitHub App)")

    # ------------------------------------------------------------------
    # HTML frontend
    # ------------------------------------------------------------------

    _html_path = Path(__file__).parent / "templates" / "index.html"
    _static_dir = Path(__file__).parent / "static"

    app.mount("/static", StaticFiles(directory=_static_dir), name="static")

    @app.get("/", response_class=HTMLResponse)
    async def index():
        """Serve the plain-HTML chat frontend."""
        return HTMLResponse(_html_path.read_text(encoding="utf-8"))

    # ------------------------------------------------------------------
    # OAuth flow
    # ------------------------------------------------------------------

    @app.get("/auth/login")
    async def auth_login():
        """Redirect the user to the GitHub OAuth authorization page."""
        state = secrets.token_urlsafe(32)
        # Store state temporarily; in production use a cache / DB
        sid = secrets.token_urlsafe(16)
        _sessions[sid] = {"oauth_state": state, "created_at": time.time()}
        params = {
            "client_id": settings.github_client_id,
            "redirect_uri": "",  # will be filled by GitHub based on app config
            "state": state,
            "scope": "copilot",
        }
        # Remove empty redirect_uri so GitHub uses the configured one
        params = {k: v for k, v in params.items() if v}
        url = (
            f"{GITHUB_AUTHORIZE_URL}?{'&'.join(f'{k}={v}' for k, v in params.items())}"
        )

        response = RedirectResponse(url=url)
        response.set_cookie(
            "session_id",
            _sign(sid, settings.session_secret),
            httponly=True,
            samesite="lax",
            max_age=3600,
        )
        return response

    @app.get("/auth/callback")
    async def auth_callback(code: str, state: str):
        """Handle the OAuth callback from GitHub."""
        # NOTE: We trust the state param loosely for the demo; production apps
        # should validate it matches the stored value.

        # Exchange the authorization code for an access token
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                GITHUB_TOKEN_URL,
                data={
                    "client_id": settings.github_client_id,
                    "client_secret": settings.github_client_secret,
                    "code": code,
                },
                headers={"Accept": "application/json"},
            )
            if resp.status_code != 200:
                raise HTTPException(
                    status_code=502, detail="Failed to exchange code for token"
                )
            token_data = resp.json()

        access_token: str | None = token_data.get("access_token")
        if not access_token:
            raise HTTPException(
                status_code=400,
                detail=token_data.get("error_description", "No access_token returned"),
            )

        # Fetch GitHub user info
        async with httpx.AsyncClient() as client:
            user_resp = await client.get(
                GITHUB_USER_URL,
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Accept": "application/json",
                },
            )
        user_info = user_resp.json() if user_resp.status_code == 200 else {}

        # Persist into session
        sid = secrets.token_urlsafe(16)
        _sessions[sid] = {
            "github_token": access_token,
            "user_login": user_info.get("login", "unknown"),
            "user_avatar": user_info.get("avatar_url"),
            "created_at": time.time(),
        }

        response = RedirectResponse(url="/")
        response.set_cookie(
            "session_id",
            _sign(sid, settings.session_secret),
            httponly=True,
            samesite="lax",
            max_age=3600,
        )
        return response

    @app.get("/auth/logout")
    async def auth_logout():
        """Clear the session and redirect to the index."""
        response = RedirectResponse(url="/")
        response.delete_cookie("session_id")
        return response

    # ------------------------------------------------------------------
    # User info
    # ------------------------------------------------------------------

    @app.get("/api/me", response_model=UserInfo)
    async def me(request: Request):
        """Return the currently logged-in user, or 401."""
        session = _get_session(request, settings.session_secret)
        if "github_token" not in session:
            raise HTTPException(status_code=401, detail="Not authenticated")
        return UserInfo(
            login=session.get("user_login", "unknown"),
            avatar_url=session.get("user_avatar"),
        )

    # ------------------------------------------------------------------
    # Chat endpoint
    # ------------------------------------------------------------------

    @app.post("/api/chat", response_model=ChatResponse)
    async def chat(body: ChatRequest, request: Request):
        """Send a message to Copilot on behalf of the authenticated user."""
        session = _get_session(request, settings.session_secret)
        github_token: str | None = session.get("github_token")
        if not github_token:
            raise HTTPException(status_code=401, detail="Not authenticated")

        try:
            client = create_copilot_client(
                cli_url=settings.copilot_cli_url,
                github_token=github_token,
            )
            await client.start()

            copilot_session = await client.create_session(
                create_session_config(tools=[])
            )
            handler = create_event_handler(writer=logger.debug)
            copilot_session.on(handler)

            reply = await copilot_session.send_and_wait(
                create_message_options(body.message)
            )
            content = reply.data.content if reply else "(no response)"
            return ChatResponse(reply=content or "(no response)")
        except Exception as e:
            logger.exception("Copilot chat failed")
            raise HTTPException(status_code=500, detail=str(e)) from e

    # ------------------------------------------------------------------
    # Report endpoint
    # ------------------------------------------------------------------

    @app.post("/api/report", response_model=ReportOutput)
    async def report(body: ReportRequest, request: Request):
        """Run multiple queries in parallel and return a structured report."""
        session = _get_session(request, settings.session_secret)
        github_token: str | None = session.get("github_token")
        if not github_token:
            raise HTTPException(status_code=401, detail="Not authenticated")

        try:
            result = await run_parallel_chat(
                cli_url=settings.copilot_cli_url,
                queries=body.queries,
                system_prompt=body.system_prompt,
                writer=logger.debug,
                github_token=github_token,
            )
            return result
        except Exception as e:
            logger.exception("Report generation failed")
            raise HTTPException(status_code=500, detail=str(e)) from e

    return app
