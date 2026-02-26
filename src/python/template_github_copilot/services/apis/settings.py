"""Backward-compatible re-export.

The canonical location is ``template_github_copilot.settings.oauth``.
"""

from template_github_copilot.settings.oauth import OAuthSettings, get_oauth_settings

__all__ = ["OAuthSettings", "get_oauth_settings"]
