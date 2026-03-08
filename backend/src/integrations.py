"""Google APIs integration for household (Calendar, Gmail, Drive).

Provides clients for Google services with household-level access.
Each service maintains its own connection and token management.
"""

from __future__ import annotations

from typing import Optional, Any
import logging

from src.oauth import OAuthToken

logger = logging.getLogger(__name__)


class GoogleCalendarClient:
    """Google Calendar API client for household event management."""

    def __init__(self, token: OAuthToken):
        self.token = token
        self.service = None
        self._build_service()

    def _build_service(self) -> None:
        """Build Google Calendar service client.
        
        Lazy import to avoid importing google-api-python-client
        unless the integration is actually used.
        """
        from googleapiclient.discovery import build
        
        self.service = build(
            "calendar",
            "v3",
            credentials=self._create_credentials(),
        )

    def _create_credentials(self) -> Any:
        """Create credentials object from token.
        
        Returns a mock credentials object that includes the access token.
        In production, would use google.oauth2.credentials.Credentials.
        """
        class TokenCredentials:
            def __init__(self, access_token: str):
                self.token = access_token
                self.expired = False
                self.valid = True
        
        return TokenCredentials(self.token.access_token)

    async def list_events(
        self,
        time_min: Optional[str] = None,
        time_max: Optional[str] = None,
        max_results: int = 10,
    ) -> list[dict]:
        """List household calendar events.
        
        Args:
            time_min: Minimum time (RFC 3339 format)
            time_max: Maximum time (RFC 3339 format)
            max_results: Max events to return
            
        Returns:
            List of calendar events
        """
        try:
            events_result = self.service.events().list(
                calendarId="primary",
                timeMin=time_min,
                timeMax=time_max,
                maxResults=max_results,
                singleEvents=True,
                orderBy="startTime",
            ).execute()
            
            return events_result.get("items", [])
        except Exception as e:
            logger.error(f"Failed to list calendar events: {e}")
            return []

    async def create_event(
        self,
        summary: str,
        start_time: str,
        end_time: Optional[str] = None,
        description: Optional[str] = None,
        attendees: Optional[list[str]] = None,
        reminders: Optional[list[dict]] = None,
    ) -> Optional[dict]:
        """Create a household calendar event.
        
        Args:
            summary: Event title
            start_time: Start time (RFC 3339)
            end_time: End time (RFC 3339)
            description: Event description
            attendees: List of attendee emails
            reminders: List of reminder configs
            
        Returns:
            Created event or None on error
        """
        try:
            event = {
                "summary": summary,
                "start": {"dateTime": start_time, "timeZone": "UTC"},
                "description": description or "",
            }
            
            if end_time:
                event["end"] = {"dateTime": end_time, "timeZone": "UTC"}
            
            if attendees:
                event["attendees"] = [{"email": email} for email in attendees]
            
            if reminders:
                event["reminders"] = {"useDefault": False, "overrides": reminders}
            
            created_event = self.service.events().insert(
                calendarId="primary",
                body=event,
            ).execute()
            
            logger.info(f"Created calendar event: {summary}")
            return created_event
        except Exception as e:
            logger.error(f"Failed to create calendar event: {e}")
            return None


class GoogleGmailClient:
    """Google Gmail API client for household email management."""

    def __init__(self, token: OAuthToken):
        self.token = token
        self.service = None
        self._build_service()

    def _build_service(self) -> None:
        """Build Gmail service client."""
        from googleapiclient.discovery import build
        
        self.service = build(
            "gmail",
            "v1",
            credentials=self._create_credentials(),
        )

    def _create_credentials(self) -> Any:
        """Create credentials object from token."""
        class TokenCredentials:
            def __init__(self, access_token: str):
                self.token = access_token
                self.expired = False
                self.valid = True
        
        return TokenCredentials(self.token.access_token)

    async def list_messages(
        self,
        query: str = "",
        max_results: int = 10,
    ) -> list[dict]:
        """List household emails.
        
        Args:
            query: Gmail search query
            max_results: Max messages to return
            
        Returns:
            List of message summaries
        """
        try:
            results = self.service.users().messages().list(
                userId="me",
                q=query,
                maxResults=max_results,
            ).execute()
            
            messages = results.get("messages", [])
            return messages
        except Exception as e:
            logger.error(f"Failed to list emails: {e}")
            return []

    async def get_message(self, message_id: str) -> Optional[dict]:
        """Get full message details.
        
        Args:
            message_id: Gmail message ID
            
        Returns:
            Message details or None
        """
        try:
            message = self.service.users().messages().get(
                userId="me",
                id=message_id,
                format="full",
            ).execute()
            
            return message
        except Exception as e:
            logger.error(f"Failed to get message {message_id}: {e}")
            return None

    async def send_message(
        self,
        to: str,
        subject: str,
        body: str,
        cc: Optional[list[str]] = None,
        bcc: Optional[list[str]] = None,
    ) -> Optional[str]:
        """Send an email from household account.
        
        Args:
            to: Recipient email
            subject: Email subject
            body: Email body (plain text)
            cc: CC addresses
            bcc: BCC addresses
            
        Returns:
            Message ID or None on error
        """
        try:
            import base64
            from email.mime.text import MIMEText
            
            message = MIMEText(body)
            message["to"] = to
            message["subject"] = subject
            
            if cc:
                message["cc"] = ", ".join(cc)
            if bcc:
                message["bcc"] = ", ".join(bcc)
            
            raw_message = base64.urlsafe_b64encode(
                message.as_bytes()
            ).decode()
            
            sent = self.service.users().messages().send(
                userId="me",
                body={"raw": raw_message},
            ).execute()
            
            logger.info(f"Sent email to {to}: {subject}")
            return sent.get("id")
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return None


class GoogleDriveClient:
    """Google Drive API client for household document management."""

    def __init__(self, token: OAuthToken):
        self.token = token
        self.service = None
        self._build_service()

    def _build_service(self) -> None:
        """Build Google Drive service client."""
        from googleapiclient.discovery import build
        
        self.service = build(
            "drive",
            "v3",
            credentials=self._create_credentials(),
        )

    def _create_credentials(self) -> Any:
        """Create credentials object from token."""
        class TokenCredentials:
            def __init__(self, access_token: str):
                self.token = access_token
                self.expired = False
                self.valid = True
        
        return TokenCredentials(self.token.access_token)

    async def list_files(
        self,
        query: str = "",
        max_results: int = 10,
    ) -> list[dict]:
        """List household Drive files.
        
        Args:
            query: File search query
            max_results: Max files to return
            
        Returns:
            List of file metadata
        """
        try:
            results = self.service.files().list(
                q=query,
                spaces="drive",
                fields="files(id, name, mimeType, parents, createdTime, modifiedTime)",
                pageSize=max_results,
            ).execute()
            
            return results.get("files", [])
        except Exception as e:
            logger.error(f"Failed to list Drive files: {e}")
            return []

    async def get_file_content(self, file_id: str) -> Optional[str]:
        """Get file content (for documents/text files).
        
        Args:
            file_id: Google Drive file ID
            
        Returns:
            File content or None
        """
        try:
            from googleapiclient.http import MediaIoBaseDownload
            import io
            
            request = self.service.files().get_media(fileId=file_id)
            file_content = io.BytesIO()
            downloader = MediaIoBaseDownload(file_content, request)
            
            done = False
            while not done:
                status, done = downloader.next_chunk()
            
            return file_content.getvalue().decode("utf-8", errors="ignore")
        except Exception as e:
            logger.error(f"Failed to get file content: {e}")
            return None

    async def create_document(
        self,
        title: str,
        body: str,
        folder_id: Optional[str] = None,
    ) -> Optional[str]:
        """Create a Google Doc in household Drive.
        
        Args:
            title: Document title
            body: Document content
            folder_id: Parent folder ID
            
        Returns:
            Document ID or None
        """
        try:
            file_metadata = {
                "name": title,
                "mimeType": "application/vnd.google-apps.document",
            }
            if folder_id:
                file_metadata["parents"] = [folder_id]
            
            # Note: This is a simplified flow. Production would use
            # Google Docs API for richer document creation.
            created = self.service.files().create(
                body=file_metadata,
                fields="id",
            ).execute()
            
            logger.info(f"Created document: {title}")
            return created.get("id")
        except Exception as e:
            logger.error(f"Failed to create document: {e}")
            return None
