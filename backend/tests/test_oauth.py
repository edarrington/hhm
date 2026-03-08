"""Tests for OAuth and integration modules."""

import pytest
from src.oauth import OAuthToken, IntegrationConfig, GoogleOAuthClient, TodoistOAuthClient
from datetime import datetime, timedelta


def test_oauth_token_creation():
    """Test creating an OAuth token."""
    token = OAuthToken(
        access_token="test_access",
        refresh_token="test_refresh",
    )
    
    assert token.access_token == "test_access"
    assert token.refresh_token == "test_refresh"
    assert token.token_type == "Bearer"


def test_oauth_token_not_expired():
    """Test token expiration check."""
    future_time = datetime.utcnow() + timedelta(hours=1)
    token = OAuthToken(
        access_token="test",
        expires_at=future_time,
    )
    
    assert not token.is_expired()


def test_oauth_token_expired():
    """Test expired token detection."""
    past_time = datetime.utcnow() - timedelta(hours=1)
    token = OAuthToken(
        access_token="test",
        expires_at=past_time,
    )
    
    assert token.is_expired()


def test_oauth_token_expiring_soon():
    """Test token expiring soon detection."""
    soon_time = datetime.utcnow() + timedelta(minutes=2)
    token = OAuthToken(
        access_token="test",
        expires_at=soon_time,
    )
    
    assert token.is_expiring_soon(minutes=5)


def test_integration_config_validation():
    """Test integration config validation."""
    # Valid Google config
    google_config = IntegrationConfig(
        service="google_calendar",
        household_id="test-household",
        client_id="test_id",
        client_secret="test_secret",
    )
    assert google_config.validate()
    
    # Valid Todoist config
    todoist_config = IntegrationConfig(
        service="todoist",
        household_id="test-household",
        api_key="test_key",
    )
    assert todoist_config.validate()


def test_integration_config_invalid():
    """Test invalid integration config."""
    invalid_config = IntegrationConfig(
        service="google_calendar",
        household_id="test-household",
        # Missing client_id and client_secret
    )
    assert not invalid_config.validate()


def test_google_oauth_client_creation():
    """Test creating Google OAuth client."""
    config = IntegrationConfig(
        service="google_calendar",
        household_id="test-household",
        client_id="test_id",
        client_secret="test_secret",
        scopes=["https://www.googleapis.com/auth/calendar"],
    )
    
    client = GoogleOAuthClient(config)
    assert client.config.service == "google_calendar"


def test_google_authorization_url():
    """Test generating Google OAuth authorization URL."""
    config = IntegrationConfig(
        service="google_calendar",
        household_id="test-household",
        client_id="test_id",
        client_secret="test_secret",
        scopes=["https://www.googleapis.com/auth/calendar"],
    )
    
    client = GoogleOAuthClient(config)
    auth_url = client.get_authorization_url("test_state")
    
    assert "accounts.google.com" in auth_url
    assert "test_id" in auth_url
    assert "test_state" in auth_url
    assert "offline" in auth_url


def test_todoist_oauth_client_creation():
    """Test creating Todoist OAuth client."""
    config = IntegrationConfig(
        service="todoist",
        household_id="test-household",
        client_id="test_id",
        client_secret="test_secret",
    )
    
    client = TodoistOAuthClient(config)
    assert client.config.service == "todoist"


def test_todoist_authorization_url():
    """Test generating Todoist OAuth authorization URL."""
    config = IntegrationConfig(
        service="todoist",
        household_id="test-household",
        client_id="test_id",
        client_secret="test_secret",
    )
    
    client = TodoistOAuthClient(config)
    auth_url = client.get_authorization_url("test_state")
    
    assert "todoist.com" in auth_url
    assert "test_id" in auth_url
    assert "test_state" in auth_url
