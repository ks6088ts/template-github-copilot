#!/usr/bin/env python3
"""BYOK (Bring Your Own Key) — Use Azure OpenAI with the GitHub Copilot SDK.

What you will learn:
    - How to configure a ProviderConfig to point to Azure OpenAI
    - How to pass an API key or bearer token to the Copilot SDK
    - How BYOK differs from the default Copilot backend

Usage (run from ``src/python``):
    # API-key authentication
    export BYOK_BASE_URL="https://<resource>.openai.azure.com/openai/deployments/<deploy>"
    export BYOK_API_KEY="<your-azure-openai-api-key>"
    export BYOK_MODEL="gpt-4o"
    uv run python scripts/tutorials/06_byok_azure_openai.py --prompt "Hello from Azure OpenAI!"

    # Bearer-token authentication (Entra ID / Managed Identity)
    export BYOK_BASE_URL="https://<resource>.openai.azure.com/openai/deployments/<deploy>"
    export BYOK_MODEL="gpt-4o"
    uv run python scripts/tutorials/06_byok_azure_openai.py --auth entra --prompt "Hello from Entra ID!"

Prerequisites:
    uv sync   # installs github-copilot-sdk and azure-identity (declared in pyproject.toml)

    Install and authenticate the GitHub Copilot CLI so the SDK can launch it:
        npm install -g @github/copilot            # or: gh copilot (downloads on first run)
        gh auth login                             # or: export COPILOT_GITHUB_TOKEN=...

Corresponding doc:
    docs/copilot_sdk_tutorial/tutorials/06_byok.md
"""

import argparse
import asyncio
import os
import sys

from azure.identity import DefaultAzureCredential
from copilot import (
    CopilotClient,
    ExternalServerConfig,
    SubprocessConfig,
)
from copilot.generated.session_events import (
    SessionEventType,
    PermissionRequest,
)
from copilot.session import (
    PermissionRequestResult,
    ProviderConfig,
    SystemMessageAppendConfig,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="BYOK: Use Azure OpenAI with the GitHub Copilot SDK",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--prompt",
        "-p",
        default="Briefly explain what BYOK means in the context of AI APIs.",
        help="Prompt to send",
    )
    parser.add_argument(
        "--cli-url",
        "-c",
        default=None,
        help=(
            "Optional Copilot CLI server URL (e.g. localhost:3000). "
            "When omitted, the SDK launches the copilot CLI over stdio."
        ),
    )
    parser.add_argument(
        "--auth",
        choices=["api-key", "entra"],
        default="api-key",
        help="Authentication method: api-key (default) or entra (Entra ID bearer token)",
    )
    parser.add_argument(
        "--base-url",
        default=os.environ.get("BYOK_BASE_URL", ""),
        help="Azure OpenAI deployment base URL (overrides BYOK_BASE_URL env var)",
    )
    parser.add_argument(
        "--api-key",
        default=os.environ.get("BYOK_API_KEY", ""),
        help="Azure OpenAI API key (overrides BYOK_API_KEY env var)",
    )
    parser.add_argument(
        "--model",
        default=os.environ.get("BYOK_MODEL", "gpt-4o"),
        help="Model/deployment name (overrides BYOK_MODEL env var, default: gpt-4o)",
    )
    return parser.parse_args()


def _build_entra_bearer_token() -> str:
    """Obtain an Azure Entra ID bearer token via DefaultAzureCredential."""
    scope = "https://cognitiveservices.azure.com/.default"
    credential = DefaultAzureCredential()
    return credential.get_token(scope).token


async def run(
    cli_url: str | None, prompt: str, auth: str, base_url: str, api_key: str, model: str
) -> None:
    if not base_url:
        print(
            "Error: --base-url (or BYOK_BASE_URL env var) is required for BYOK mode.",
            file=sys.stderr,
        )
        sys.exit(1)

    # ------------------------------------------------------------------
    # Build ProviderConfig
    # ------------------------------------------------------------------
    if auth == "api-key":
        if not api_key:
            print(
                "Error: --api-key (or BYOK_API_KEY env var) is required for api-key auth.",
                file=sys.stderr,
            )
            sys.exit(1)
        provider = ProviderConfig(
            type="azure",
            base_url=base_url,
            api_key=api_key,
        )
        print(f"[Auth] Using API key authentication — model: {model}")
    else:
        bearer_token = _build_entra_bearer_token()
        provider = ProviderConfig(
            type="azure",
            base_url=base_url,
            bearer_token=bearer_token,
        )
        print(f"[Auth] Using Entra ID bearer token — model: {model}")

    # ------------------------------------------------------------------
    # Session setup
    # ------------------------------------------------------------------

    def approve_all(
        request: PermissionRequest,
        context: dict,
    ) -> PermissionRequestResult:
        return PermissionRequestResult(kind="approved", rules=[])

    client_options: ExternalServerConfig | SubprocessConfig = (
        ExternalServerConfig(url=cli_url) if cli_url else SubprocessConfig()
    )
    client = CopilotClient(client_options)
    await client.start()

    session = await client.create_session(
        on_permission_request=approve_all,
        tools=[],
        streaming=True,
        model=model,
        provider=provider,
        system_message=SystemMessageAppendConfig(
            content="You are a helpful assistant powered by Azure OpenAI."
        ),
    )

    print(f"\nYou: {prompt}\nCopilot: ", end="")

    def on_event(event) -> None:  # noqa: ANN001
        if event.type == SessionEventType.ASSISTANT_MESSAGE_DELTA:
            print(event.data.delta_content, end="", flush=True)
        elif event.type == SessionEventType.SESSION_ERROR:
            print(f"\n[Error] {event.data.message}", file=sys.stderr)

    session.on(on_event)

    await session.send_and_wait(prompt, timeout=300)
    print()


def main() -> None:
    args = parse_args()
    try:
        asyncio.run(
            run(
                cli_url=args.cli_url,
                prompt=args.prompt,
                auth=args.auth,
                base_url=args.base_url,
                api_key=args.api_key,
                model=args.model,
            )
        )
    except KeyboardInterrupt:
        print("\nBye!")


if __name__ == "__main__":
    main()
