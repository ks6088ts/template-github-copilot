"""Tests for the FastAPI OAuth GitHub App chat application."""

import logging
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from template_github_copilot.services.apis.app import (
    ChatRequest,
    ChatResponse,
    ReportRequest,
    UserInfo,
    _sessions,
    _sign,
    _verify,
    create_app,
)
from template_github_copilot.services.reports import ReportOutput, ReportResult
from template_github_copilot.settings import OAuthSettings

logger = logging.getLogger("template_github_copilot.services.apis.app")


@pytest.fixture
def settings() -> OAuthSettings:
    """Return test-only OAuthSettings (no real credentials)."""
    return OAuthSettings(
        github_client_id="test-client-id",
        github_client_secret="test-client-secret",
        session_secret="test-secret",
        copilot_cli_url="localhost:3000",
    )


@pytest.fixture
def client(settings: OAuthSettings) -> TestClient:
    """Return a TestClient wired to the test app."""
    app = create_app(settings)
    return TestClient(app, follow_redirects=False)


@pytest.fixture(autouse=True)
def _clear_sessions():
    """Ensure session store is clean between tests."""
    _sessions.clear()
    yield
    _sessions.clear()


# ── Pydantic models ──────────────────────────────────────────────────


class TestModels:
    def test_chat_request(self):
        req = ChatRequest(message="hello")
        assert req.message == "hello"

    def test_chat_response(self):
        resp = ChatResponse(reply="world")
        assert resp.reply == "world"

    def test_user_info(self):
        info = UserInfo(login="octocat", avatar_url="https://example.com/avatar.png")
        assert info.login == "octocat"


# ── Signing helpers ──────────────────────────────────────────────────


class TestSigning:
    def test_sign_and_verify(self):
        signed = _sign("abc", "secret")
        assert _verify(signed, "secret") == "abc"

    def test_verify_bad_signature(self):
        signed = _sign("abc", "secret")
        assert _verify(signed, "wrong-secret") is None

    def test_verify_malformed(self):
        assert _verify("no-dot-here", "secret") is None


# ── Routes ───────────────────────────────────────────────────────────


class TestIndex:
    def test_index_returns_html(self, client: TestClient):
        resp = client.get("/")
        assert resp.status_code == 200
        assert "text/html" in resp.headers["content-type"]
        assert "template-github-copilot" in resp.text


class TestAuthLogin:
    def test_login_redirects_to_github(self, client: TestClient):
        resp = client.get("/auth/login")
        assert resp.status_code == 307
        location = resp.headers["location"]
        assert "github.com/login/oauth/authorize" in location
        assert "client_id=test-client-id" in location


class TestAuthCallback:
    @patch("template_github_copilot.services.apis.app.httpx.AsyncClient")
    def test_callback_success(self, mock_async_client_cls, client: TestClient):
        """Simulate a successful OAuth callback."""
        # Mock httpx responses
        token_response = MagicMock()
        token_response.status_code = 200
        token_response.json.return_value = {"access_token": "gho_test123"}

        user_response = MagicMock()
        user_response.status_code = 200
        user_response.json.return_value = {
            "login": "testuser",
            "avatar_url": "https://example.com/avatar.png",
        }

        mock_client_instance = AsyncMock()
        mock_client_instance.post.return_value = token_response
        mock_client_instance.get.return_value = user_response
        mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance)
        mock_client_instance.__aexit__ = AsyncMock(return_value=False)
        mock_async_client_cls.return_value = mock_client_instance

        resp = client.get("/auth/callback?code=test-code&state=test-state")
        assert resp.status_code == 307
        assert resp.headers["location"] == "/"
        assert "session_id" in resp.cookies

    @patch("template_github_copilot.services.apis.app.httpx.AsyncClient")
    def test_callback_token_exchange_failure(
        self, mock_async_client_cls, client: TestClient
    ):
        token_response = MagicMock()
        token_response.status_code = 500

        mock_client_instance = AsyncMock()
        mock_client_instance.post.return_value = token_response
        mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance)
        mock_client_instance.__aexit__ = AsyncMock(return_value=False)
        mock_async_client_cls.return_value = mock_client_instance

        resp = client.get("/auth/callback?code=bad-code&state=s")
        assert resp.status_code == 502


class TestAuthLogout:
    def test_logout_redirects_and_clears_cookie(self, client: TestClient):
        resp = client.get("/auth/logout")
        assert resp.status_code == 307
        assert resp.headers["location"] == "/"


class TestMe:
    def test_me_unauthenticated(self, client: TestClient):
        resp = client.get("/api/me")
        assert resp.status_code == 401

    def test_me_authenticated(self, client: TestClient, settings: OAuthSettings):
        # Manually insert a session
        sid = "test-sid"
        _sessions[sid] = {
            "github_token": "gho_fake",
            "user_login": "octocat",
            "user_avatar": "https://example.com/avatar.png",
        }
        signed_cookie = _sign(sid, settings.session_secret)
        client.cookies.set("session_id", signed_cookie)

        resp = client.get("/api/me")
        assert resp.status_code == 200
        data = resp.json()
        assert data["login"] == "octocat"


class TestChat:
    def test_chat_unauthenticated(self, client: TestClient):
        resp = client.post("/api/chat", json={"message": "hi"})
        assert resp.status_code == 401

    @patch("template_github_copilot.services.apis.app.create_copilot_client")
    @patch(
        "template_github_copilot.services.apis.app.create_message_options",
        return_value="opts",
    )
    @patch("template_github_copilot.services.apis.app.create_event_handler")
    @patch("template_github_copilot.services.apis.app.create_session_config")
    def test_chat_authenticated(
        self,
        mock_create_session_config,
        mock_create_event_handler,
        mock_create_message_options,
        mock_create_copilot_client,
        client: TestClient,
        settings: OAuthSettings,
    ):
        """Verify chat endpoint calls CopilotClient with the user's token."""
        # Set up session
        sid = "chat-sid"
        _sessions[sid] = {"github_token": "gho_chat_token", "user_login": "dev"}
        signed_cookie = _sign(sid, settings.session_secret)
        client.cookies.set("session_id", signed_cookie)

        # Mock CopilotClient
        mock_reply = MagicMock()
        mock_reply.data.content = "Hello from Copilot!"

        mock_session = AsyncMock()
        mock_session.send_and_wait.return_value = mock_reply

        mock_client = AsyncMock()
        mock_client.start = AsyncMock()
        mock_client.create_session = AsyncMock(return_value=mock_session)
        mock_create_copilot_client.return_value = mock_client

        resp = client.post("/api/chat", json={"message": "hi"})

        assert resp.status_code == 200
        assert resp.json()["reply"] == "Hello from Copilot!"


class TestReport:
    def test_report_unauthenticated(self, client: TestClient):
        resp = client.post(
            "/api/report",
            json={"queries": ["q1"], "system_prompt": "Be helpful"},
        )
        assert resp.status_code == 401

    @patch("template_github_copilot.services.apis.app.run_parallel_chat")
    def test_report_authenticated(
        self,
        mock_run_parallel_chat,
        client: TestClient,
        settings: OAuthSettings,
    ):
        """Verify report endpoint calls run_parallel_chat with the user's token."""
        sid = "report-sid"
        _sessions[sid] = {"github_token": "gho_report_token", "user_login": "dev"}
        signed_cookie = _sign(sid, settings.session_secret)
        client.cookies.set("session_id", signed_cookie)

        mock_run_parallel_chat.return_value = ReportOutput(
            system_prompt="Be helpful",
            results=[
                ReportResult(query="q1", response="answer1"),
                ReportResult(query="q2", response="answer2"),
            ],
            total=2,
            succeeded=2,
            failed=0,
        )

        resp = client.post(
            "/api/report",
            json={"queries": ["q1", "q2"], "system_prompt": "Be helpful"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 2
        assert data["succeeded"] == 2
        assert data["failed"] == 0
        assert len(data["results"]) == 2
        assert data["results"][0]["query"] == "q1"
        assert data["results"][0]["response"] == "answer1"

        mock_run_parallel_chat.assert_called_once_with(
            cli_url="localhost:3000",
            queries=["q1", "q2"],
            system_prompt="Be helpful",
            writer=logger.debug,
            github_token="gho_report_token",
        )

    @patch("template_github_copilot.services.apis.app.run_parallel_chat")
    def test_report_failure(
        self,
        mock_run_parallel_chat,
        client: TestClient,
        settings: OAuthSettings,
    ):
        """Verify report endpoint returns 500 when run_parallel_chat raises."""
        sid = "report-err-sid"
        _sessions[sid] = {"github_token": "gho_err_token", "user_login": "dev"}
        signed_cookie = _sign(sid, settings.session_secret)
        client.cookies.set("session_id", signed_cookie)

        mock_run_parallel_chat.side_effect = RuntimeError("boom")

        resp = client.post(
            "/api/report",
            json={"queries": ["q1"], "system_prompt": "Be helpful"},
        )
        assert resp.status_code == 500

    def test_report_request_model(self):
        req = ReportRequest(queries=["q1", "q2"], system_prompt="prompt")
        assert req.queries == ["q1", "q2"]
        assert req.system_prompt == "prompt"
