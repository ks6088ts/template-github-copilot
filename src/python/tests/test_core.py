"""Tests for template_github_copilot.core module.

Functions that depend heavily on the copilot SDK are tested with mocks.
"""

import types
from unittest.mock import MagicMock

import typer
from copilot.generated.session_events import SessionEventType

from template_github_copilot.core import (
    _default_writer,
    _get_system_message,
    approve_all,
    create_copilot_client,
    create_event_handler,
    create_message_options,
    create_session_config,
    write_status,
)


# ---------------------------------------------------------------------------
# write_status
# ---------------------------------------------------------------------------


def test_write_status_calls_writer():
    """write_status should call the writer with a formatted message."""
    messages: list[str] = []
    write_status("Label", typer.colors.GREEN, "hello", writer=messages.append)
    assert len(messages) == 1
    assert "Label" in messages[0]
    assert "hello" in messages[0]


def test_write_status_default_writer(capsys):
    """write_status with default writer should print to stdout."""
    write_status("Test", typer.colors.BLUE, "world")
    captured = capsys.readouterr()
    assert "Test" in captured.out
    assert "world" in captured.out


# ---------------------------------------------------------------------------
# _default_writer
# ---------------------------------------------------------------------------


def test_default_writer(capsys):
    """_default_writer should print the message."""
    _default_writer("output")
    captured = capsys.readouterr()
    assert "output" in captured.out


# ---------------------------------------------------------------------------
# _get_system_message
# ---------------------------------------------------------------------------


def test_get_system_message():
    """_get_system_message should return a SystemMessageAppendConfig dict."""
    msg = _get_system_message()
    # SystemMessageAppendConfig is a TypedDict, so check contents directly
    assert "content" in msg
    assert "helpful assistant" in msg["content"].lower()


# ---------------------------------------------------------------------------
# approve_all
# ---------------------------------------------------------------------------


def test_approve_all():
    """approve_all should return an approved result."""
    request = MagicMock()
    result = approve_all(request, {})
    assert result["kind"] == "approved"
    assert result["rules"] == []


# ---------------------------------------------------------------------------
# create_copilot_client
# ---------------------------------------------------------------------------


def test_create_copilot_client():
    """create_copilot_client should return a CopilotClient."""
    client = create_copilot_client("localhost:4000")
    assert client is not None


def test_create_copilot_client_default():
    """create_copilot_client with default url."""
    client = create_copilot_client()
    assert client is not None


# ---------------------------------------------------------------------------
# create_session_config
# ---------------------------------------------------------------------------


def test_create_session_config_defaults():
    """create_session_config should produce a valid SessionConfig."""
    config = create_session_config()
    assert "on_permission_request" in config
    assert "streaming" in config
    assert config["streaming"] is True


def test_create_session_config_no_system_message():
    """create_session_config with system_message=None should not set system_message."""
    config = create_session_config(system_message=None)
    assert "system_message" not in config


def test_create_session_config_with_custom_tools():
    """create_session_config should accept custom tools."""
    config = create_session_config(tools=[])
    assert config["tools"] == []


def test_create_session_config_none_tools():
    """create_session_config with tools=None should set empty list."""
    config = create_session_config(tools=None)
    assert config["tools"] == []


def test_create_session_config_streaming_false():
    """create_session_config with streaming=False."""
    config = create_session_config(streaming=False)
    assert config["streaming"] is False


# ---------------------------------------------------------------------------
# create_message_options
# ---------------------------------------------------------------------------


def test_create_message_options():
    """create_message_options should return a MessageOptions with the given prompt."""
    opts = create_message_options("test prompt")
    assert opts["prompt"] == "test prompt"


def test_create_message_options_empty():
    """create_message_options with empty prompt."""
    opts = create_message_options("")
    assert opts["prompt"] == ""


# ---------------------------------------------------------------------------
# create_event_handler
# ---------------------------------------------------------------------------


def _make_event(event_type, **data_kwargs):
    """Helper to build a fake event."""
    data = types.SimpleNamespace(**data_kwargs)
    return types.SimpleNamespace(type=event_type, data=data)


def test_event_handler_assistant_turn_start():
    messages: list[str] = []
    handler = create_event_handler(writer=messages.append)
    handler(_make_event(SessionEventType.ASSISTANT_TURN_START))
    assert any("thinking" in m.lower() for m in messages)


def test_event_handler_assistant_intent():
    messages: list[str] = []
    handler = create_event_handler(writer=messages.append)
    handler(_make_event(SessionEventType.ASSISTANT_INTENT, intent="search"))
    assert any("search" in m for m in messages)


def test_event_handler_assistant_turn_end():
    messages: list[str] = []
    handler = create_event_handler(writer=messages.append)
    handler(_make_event(SessionEventType.ASSISTANT_TURN_END))
    assert any("finished" in m.lower() for m in messages)


def test_event_handler_tool_execution_start():
    messages: list[str] = []
    handler = create_event_handler(writer=messages.append)
    handler(_make_event(SessionEventType.TOOL_EXECUTION_START, tool_name="my_tool"))
    assert any("my_tool" in m for m in messages)


def test_event_handler_tool_execution_progress():
    messages: list[str] = []
    handler = create_event_handler(writer=messages.append)
    handler(
        _make_event(SessionEventType.TOOL_EXECUTION_PROGRESS, progress_message="50%")
    )
    assert any("50%" in m for m in messages)


def test_event_handler_tool_execution_complete_success():
    messages: list[str] = []
    handler = create_event_handler(writer=messages.append)
    result = types.SimpleNamespace(content="done")
    handler(_make_event(SessionEventType.TOOL_EXECUTION_COMPLETE, result=result))
    assert any("done" in m for m in messages)


def test_event_handler_tool_execution_complete_no_result():
    messages: list[str] = []
    handler = create_event_handler(writer=messages.append)
    handler(_make_event(SessionEventType.TOOL_EXECUTION_COMPLETE, result=None))
    assert any("Completed" in m for m in messages)


def test_event_handler_tool_execution_complete_error():
    messages: list[str] = []
    handler = create_event_handler(writer=messages.append)
    error = types.SimpleNamespace(message="something went wrong")
    handler(
        _make_event(SessionEventType.TOOL_EXECUTION_COMPLETE, error=error, result=None)
    )
    assert any("something went wrong" in m for m in messages)


def test_event_handler_assistant_message_delta():
    messages: list[str] = []
    handler = create_event_handler(writer=messages.append)
    handler(_make_event(SessionEventType.ASSISTANT_MESSAGE_DELTA, delta_content="hi"))
    assert any("hi" in m for m in messages)


def test_event_handler_session_error():
    messages: list[str] = []
    handler = create_event_handler(writer=messages.append)
    handler(_make_event(SessionEventType.SESSION_ERROR, message="Oops"))
    assert any("Oops" in m for m in messages)


def test_event_handler_session_idle():
    messages: list[str] = []
    handler = create_event_handler(writer=messages.append)
    handler(_make_event(SessionEventType.SESSION_IDLE))
    assert any("completed" in m.lower() for m in messages)


def test_event_handler_session_idle_calls_callback():
    """on_session_idle callback should be invoked."""
    called = []
    handler = create_event_handler(
        writer=lambda _: None,
        on_session_idle=lambda: called.append(True),
    )
    handler(_make_event(SessionEventType.SESSION_IDLE))
    assert called == [True]


def test_event_handler_unknown_event_no_error():
    """Unknown event types should be silently ignored."""
    messages: list[str] = []
    handler = create_event_handler(writer=messages.append)
    handler(_make_event("UNKNOWN_EVENT_TYPE"))
    # Should not raise and may or may not produce output
