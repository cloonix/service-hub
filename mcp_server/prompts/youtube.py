"""YouTube-related prompts for MCP server."""


def register_youtube_prompts(mcp_server):
    """Register YouTube-related MCP prompts.

    Args:
        mcp_server: FastMCP server instance
    """

    @mcp_server.prompt()
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
