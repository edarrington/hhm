"""OAuth and integration management for household accounts.

Handles Google OAuth, token management, and integration setup for
household-level access to Google APIs and Todoist.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional
import logging

from src.config import get_settings

logger = logging.getLogger(__name__)


@dataclass
class OAuthToken:
    """OAuth token for an integration."""

    access_token: str
    refresh_token: Optional[str] = None
    expires_at: Optional[datetime] = None
    token_type: str = "Bearer"

    def is_expired(self) -> bool:
        """Check if token is expired."""
        if not self.expires_at:
            return False
        return datetime.utcnow() >= self.expires_at

    def is_expiring_soon(self, minutes: int = 5) -> bool:
        """Check if token will expire soon."""
        if not self.expires_at:
            return False
        return datetime.utcnow() >= (self.expires_at - timedelta(minutes=minutes))


@dataclass
class IntegrationConfig:
    """Configuration for an integration."""

    service: str  # google_calendar, google_gmail, google_drive, todoist
    household_id: str
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    api_key: Optional[str] = None
    scopes: Optional[list[str]] = None

    def validate(self) -> bool:
        """Validate configuration has required fields."""
        if not self.service or not self.household_id:
            return False
        if self.service.startswith("google_"):
            return bool(self.client_id and self.client_secret)
        if self.service == "todoist":
            return bool(self.api_key)
        return False


class GoogleOAuthClient:
    """Manages Google OAuth flow for household accounts."""

    def __init__(self, config: IntegrationConfig):
        self.config = config
        self.settings = get_settings()

    def get_authorization_url(self, state: str) -> str:
        """Generate OAuth authorization URL for household.
        
        Args:
            state: CSRF protection token
            
        Returns:
            Authorization URL for user to visit
        """
        params = {
            "client_id": self.config.client_id,
            "redirect_uri": self.settings.google_redirect_uri,
            "response_type": "code",
            "scope": " ".join(self.config.scopes or []),
            "state": state,
            "access_type": "offline",
            "prompt": "consent",
        }
        
        query_string = "&".join(f"{k}={v}" for k, v in params.items())
        return f"https://accounts.google.com/o/oauth2/v2/auth?{query_string}"

    async def exchange_code_for_token(self, code: str) -> OAuthToken:
        """Exchange authorization code for access token.
        
        Args:
            code: Authorization code from OAuth flow
            
        Returns:
            OAuthToken with access and refresh tokens
        """
        import httpx
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "client_id": self.config.client_id,
                    "client_secret": self.config.client_secret,
                    "code": code,
                    "grant_type": "authorization_code",
                    "redirect_uri": self.settings.google_redirect_uri,
                },
            )
            response.raise_for_status()
            data = response.json()
            
            expires_at = None
            if "expires_in" in data:
                expires_at = datetime.utcnow() + timedelta(seconds=data["expires_in"])
            
            return OAuthToken(
                access_token=data["access_token"],
                refresh_token=data.get("refresh_token"),
                expires_at=expires_at,
            )

    async def refresh_access_token(self, refresh_token: str) -> OAuthToken:
        """Refresh access token using refresh token.
        
        Args:
            refresh_token: Refresh token from previous OAuth flow
            
        Returns:
            New OAuthToken with refreshed access token
        """
        import httpx
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "client_id": self.config.client_id,
                    "client_secret": self.config.client_secret,
                    "refresh_token": refresh_token,
                    "grant_type": "refresh_token",
                },
            )
            response.raise_for_status()
            data = response.json()
            
            expires_at = None
            if "expires_in" in data:
                expires_at = datetime.utcnow() + timedelta(seconds=data["expires_in"])
            
            return OAuthToken(
                access_token=data["access_token"],
                refresh_token=refresh_token,
                expires_at=expires_at,
            )


class TodoistOAuthClient:
    """Manages Todoist OAuth flow for household accounts."""

    def __init__(self, config: IntegrationConfig):
        self.config = config
        self.settings = get_settings()

    def get_authorization_url(self, state: str) -> str:
        """Generate Todoist OAuth authorization URL.
        
        Args:
            state: CSRF protection token
            
        Returns:
            Authorization URL for user to visit
        """
        params = {
            "client_id": self.config.client_id,
            "scope": "data:read_write,project:read_write,task:read_write",
            "state": state,
            "redirect_uri": self.settings.todoist_redirect_uri,
        }
        
        query_string = "&".join(f"{k}={v}" for k, v in params.items())
        return f"https://todoist.com/oauth/authorize?{query_string}"

    async def exchange_code_for_token(self, code: str) -> OAuthToken:
        """Exchange authorization code for Todoist API token.
        
        Args:
            code: Authorization code from OAuth flow
            
        Returns:
            OAuthToken with access token
        """
        import httpx
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://todoist.com/oauth/access_token",
                data={
                    "client_id": self.config.client_id,
                    "client_secret": self.config.client_secret,
                    "code": code,
                    "grant_type": "authorization_code",
                    "redirect_uri": self.settings.todoist_redirect_uri,
                },
            )
            response.raise_for_status()
            data = response.json()
            
            return OAuthToken(
                access_token=data["access_token"],
                token_type=data.get("token_type", "Bearer"),
            )
