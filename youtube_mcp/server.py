"""MCP Server for YouTube Transcript Service.

This MCP server exposes YouTube transcript functionality to LLMs via the Model Context Protocol.
It acts as a client to the FastAPI backend, using the master API key for authentication.
"""

import asyncio
import logging
import os
from typing import Any

from mcp.server.fastmcp import FastMCP

from youtube_mcp.client import YouTubeAPIClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Initialize MCP server
mcp = FastMCP("YouTube Transcript Service")

# Initialize API client (lazy-loaded on first use)
_api_client: YouTubeAPIClient | None = None


def get_api_client() -> YouTubeAPIClient:
    """Get or create API client instance.

    Returns:
        YouTubeAPIClient instance
    """
    global _api_client
    if _api_client is None:
        api_url = os.getenv("FASTAPI_URL", "http://api:8000")
        api_key = os.getenv("MCP_API_KEY") or os.getenv("MASTER_API_KEY", "")

        if not api_key:
            raise ValueError(
                "MCP_API_KEY or MASTER_API_KEY must be set in environment variables"
            )

        _api_client = YouTubeAPIClient(base_url=api_url, api_key=api_key)
        logger.info(f"Initialized YouTube API client with base URL: {api_url}")

    return _api_client


@mcp.tool()
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
    client = get_api_client()

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


@mcp.tool()
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
    client = get_api_client()

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


@mcp.resource("info://youtube-service")
def get_service_info() -> str:
    """Get information about the YouTube Transcript Service.

    Returns:
        Service information as formatted text
    """
    return """YouTube Transcript Service (via MCP)

This service provides access to YouTube video transcripts through the Model Context Protocol.

Available Tools:
- get_youtube_transcript: Fetch transcript for a video
- list_youtube_languages: List available transcript languages

Supported Formats:
- plain: Plain text transcript
- structured: JSON with timestamps and text
- srt: SubRip subtitle format
- vtt: WebVTT subtitle format

Features:
- Automatic caching for faster repeated requests
- Support for multiple languages
- Auto-generated and manual transcripts
- Rate limiting based on API key tier

Example Usage:
1. List available languages: list_youtube_languages("dQw4w9WgXcQ")
2. Get transcript: get_youtube_transcript("dQw4w9WgXcQ", languages=["en"], format_type="plain")
"""


@mcp.prompt()
def summarize_video(video_url: str, focus: str = "general") -> str:
    """Generate a prompt for summarizing a YouTube video.

    Args:
        video_url: YouTube video URL or ID
        focus: What to focus on - 'general', 'technical', 'key-points', or 'action-items'

    Returns:
        A formatted prompt for the LLM to summarize the video
    """
    focus_instructions = {
        "general": "Provide a comprehensive summary of the video content.",
        "technical": "Focus on technical details, concepts, and methodologies discussed.",
        "key-points": "Extract and list the main key points and takeaways.",
        "action-items": "Identify actionable items and recommendations from the video.",
    }

    instruction = focus_instructions.get(focus, focus_instructions["general"])

    return f"""Please analyze this YouTube video and {instruction}

Video: {video_url}

First, use the get_youtube_transcript tool to fetch the transcript.
Then, analyze the content and provide your summary.
"""


def main():
    """Entry point for the MCP server."""
    # Get configuration from environment
    transport = os.getenv("MCP_TRANSPORT", "streamable-http")  # Default to HTTP

    logger.info("Starting MCP server")
    logger.info(f"Transport: {transport}")
    logger.info("YouTube Transcript Service is ready")

    # Run with HTTP transport (for remote access) or stdio (for local Claude Desktop)
    # When using streamable-http, server runs at http://0.0.0.0:8000/mcp by default
    # Use UVICORN_HOST and UVICORN_PORT environment variables to configure
    if transport == "stdio":
        mcp.run()
    else:
        mcp.run(transport="streamable-http")


if __name__ == "__main__":
    main()

# For uvicorn direct deployment
# Run with: uvicorn youtube_mcp.server:app --host 0.0.0.0 --port 8001
app = mcp.streamable_http_app()
