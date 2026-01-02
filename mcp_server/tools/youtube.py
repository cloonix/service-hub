"""YouTube transcript tools for MCP server."""

import logging
from typing import Any

from mcp_server.clients.youtube import YouTubeAPIClient

logger = logging.getLogger(__name__)


def register_youtube_tools(mcp_server, api_client_factory):
    """Register YouTube-related MCP tools.

    Args:
        mcp_server: FastMCP server instance
        api_client_factory: Function that returns YouTubeAPIClient instance
    """

    @mcp_server.tool()
    async def get_youtube_transcript(
        video_url_or_id: str,
        languages: list[str] | None = None,
        format_type: str = "plain",
    ) -> dict[str, Any]:
        """Fetch YouTube video transcript.

        Retrieves the transcript for a YouTube video in various formats.

        Args:
            video_url_or_id: YouTube video URL or video ID (e.g., 'dQw4w9WgXcQ' or 'https://youtube.com/watch?v=dQw4w9WgXcQ')
            languages: List of preferred language codes (e.g., ['en', 'es']). Defaults to ['en']
            format_type: Output format - 'plain', 'structured', 'srt', or 'vtt'. Defaults to 'plain'

        Returns:
            Dictionary containing:
                - success: Whether the request succeeded
                - video_id: Extracted video ID
                - transcript: The transcript text (format depends on format_type)
                - language: Language code of the returned transcript
                - is_generated: Whether the transcript was auto-generated
                - format: Format type used
                - cached: Whether the result was served from cache
                - error: Error message if failed

        Example:
            >>> await get_youtube_transcript("dQw4w9WgXcQ")
            {
                "success": true,
                "video_id": "dQw4w9WgXcQ",
                "transcript": "We're no strangers to love...",
                "language": "en",
                "is_generated": false,
                "format": "plain",
                "cached": false
            }
        """
        client = api_client_factory()

        try:
            result = await client.get_transcript(
                video_url_or_id=video_url_or_id,
                languages=languages or ["en"],
                format_type=format_type,
            )
            return result
        except Exception as e:
            logger.error(f"Error fetching transcript: {e}")
            return {
                "success": False,
                "error": str(e),
                "video_id": video_url_or_id,
                "transcript": None,
                "language": None,
                "is_generated": None,
                "format": format_type,
                "cached": False,
            }

    @mcp_server.tool()
    async def list_youtube_languages(video_id: str) -> dict[str, Any]:
        """List available transcript languages for a YouTube video.

        Retrieves all available transcript languages for a video, including both
        manual and auto-generated transcripts.

        Args:
            video_id: YouTube video ID (e.g., 'dQw4w9WgXcQ')

        Returns:
            Dictionary containing:
                - success: Whether the request succeeded
                - video_id: Video ID
                - languages: List of available language objects with:
                    - language: Language code (e.g., 'en')
                    - language_code: Full language code (e.g., 'en-US')
                    - is_generated: Whether it's auto-generated
                    - is_translatable: Whether it can be translated
                - error: Error message if failed

        Example:
            >>> await list_youtube_languages("dQw4w9WgXcQ")
            {
                "success": true,
                "video_id": "dQw4w9WgXcQ",
                "languages": [
                    {
                        "language": "en",
                        "language_code": "en",
                        "is_generated": false,
                        "is_translatable": true
                    }
                ]
            }
        """
        client = api_client_factory()

        try:
            result = await client.list_languages(video_id=video_id)
            return result
        except Exception as e:
            logger.error(f"Error listing languages: {e}")
            return {
                "success": False,
                "error": str(e),
                "video_id": video_id,
                "languages": [],
            }
