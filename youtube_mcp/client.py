"""HTTP client for YouTube Transcript API.

This module provides an async HTTP client to communicate with the FastAPI backend.
"""

import httpx
from typing import Any


class YouTubeAPIClient:
    """Async HTTP client for YouTube Transcript API."""

    def __init__(self, base_url: str, api_key: str, timeout: float = 30.0):
        """Initialize the API client.

        Args:
            base_url: Base URL of the FastAPI server (e.g., 'http://api:8000')
            api_key: API key for authentication
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout
        self._client: httpx.AsyncClient | None = None

    @property
    def client(self) -> httpx.AsyncClient:
        """Get or create the HTTP client.

        Returns:
            httpx.AsyncClient instance
        """
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                headers={"X-API-Key": self.api_key},
                timeout=self.timeout,
            )
        return self._client

    async def close(self):
        """Close the HTTP client."""
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    async def get_transcript(
        self,
        video_url_or_id: str,
        languages: list[str] | None = None,
        format_type: str = "plain",
    ) -> dict[str, Any]:
        """Fetch YouTube video transcript.

        Args:
            video_url_or_id: YouTube video URL or ID
            languages: List of preferred language codes
            format_type: Output format ('plain', 'structured', 'srt', 'vtt')

        Returns:
            Transcript response dictionary

        Raises:
            httpx.HTTPError: If the request fails
        """
        response = await self.client.post(
            "/api/v1/youtube/transcript",
            json={
                "video_url_or_id": video_url_or_id,
                "languages": languages or ["en"],
                "format_type": format_type,
            },
        )
        response.raise_for_status()
        return response.json()

    async def list_languages(self, video_id: str) -> dict[str, Any]:
        """List available transcript languages for a video.

        Args:
            video_id: YouTube video ID

        Returns:
            Languages response dictionary

        Raises:
            httpx.HTTPError: If the request fails
        """
        response = await self.client.get(f"/api/v1/youtube/languages/{video_id}")
        response.raise_for_status()
        return response.json()

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
