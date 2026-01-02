"""Service information resources for MCP server."""


def register_info_resources(mcp_server):
    """Register service information resources.

    Args:
        mcp_server: FastMCP server instance
    """

    @mcp_server.resource("info://service-hub")
    def get_service_info() -> str:
        """Get information about the Service Hub MCP Server.

        Returns:
            Service information as formatted text
        """
        return """Service Hub MCP Server

This MCP server provides access to multiple tools and services through the Model Context Protocol.

Available Tool Categories:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📺 YouTube Tools:
  - get_youtube_transcript: Fetch transcript for a video
  - list_youtube_languages: List available transcript languages

  Supported Formats:
    - plain: Plain text transcript
    - structured: JSON with timestamps and text

  Features:
    - Automatic caching for faster repeated requests
    - Support for multiple languages
    - Auto-generated and manual transcripts
    - Rate limiting based on API key tier

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 Available Prompts:
  - summarize_video: Generate prompts for video summarization

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Example Usage:
  1. List available languages: list_youtube_languages("dQw4w9WgXcQ")
  2. Get transcript: get_youtube_transcript("dQw4w9WgXcQ", languages=["en"], format_type="plain")
  3. Use prompt: Use 'summarize_video' prompt with a YouTube URL

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Backend API: All tools connect to the FastAPI backend which handles:
  - Authentication & API key management
  - Rate limiting per tier (free/premium/admin)
  - Caching with TTL
  - Service-specific business logic

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Note: More tools coming soon (RSS, database, file operations, etc.)
"""
