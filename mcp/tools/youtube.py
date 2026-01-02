"""YouTube transcript tools for MCP server."""

import logging
from typing import Any

from lib.youtube import TranscriptService

logger = logging.getLogger(__name__)


def register_youtube_tools(mcp_server, cache=None):
    """Register YouTube-related MCP tools.

    Args:
        mcp_server: FastMCP server instance
        cache: Optional cache instance (default: None)
    """
    # Create service instance (shared across tool invocations)
    service = TranscriptService(cache=cache)

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
            format_type: Output format - 'plain' or 'structured'. Defaults to 'plain'

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
        try:
            result = service.get_transcript(
                video_url_or_id=video_url_or_id,
                languages=languages or ["en"],
                format_type=format_type,
            )
            return result.model_dump()
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
                    - code: Language code (e.g., 'en')
                    - name: Language name (e.g., 'English')
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
                        "code": "en",
                        "name": "English",
                        "is_generated": false,
                        "is_translatable": true
                    }
                ]
            }
        """
        try:
            result = service.list_languages(video_url_or_id=video_id)
            return result.model_dump()
        except Exception as e:
            logger.error(f"Error listing languages: {e}")
            return {
                "success": False,
                "error": str(e),
                "video_id": video_id,
                "languages": [],
            }
