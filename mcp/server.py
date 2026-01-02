"""MCP Server for Service Hub.

This MCP server exposes multiple tools and services to LLMs via the Model Context Protocol.
Uses the core YouTube transcript library directly (no HTTP calls).
"""

import logging
import os

from mcp.server.fastmcp import FastMCP

from mcp.prompts import register_youtube_prompts
from mcp.resources import register_info_resources
from mcp.tools import register_youtube_tools

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Initialize MCP server
mcp = FastMCP("Service Hub")

# Register all tools, prompts, and resources
logger.info("Registering MCP tools...")
# MCP uses library directly - no cache for now (can add later if needed)
register_youtube_tools(mcp, cache=None)
logger.info("Registering MCP prompts...")
register_youtube_prompts(mcp)
logger.info("Registering MCP resources...")
register_info_resources(mcp)


def main() -> None:
    """Entry point for the MCP server."""
    # Get configuration from environment
    transport = os.getenv("MCP_TRANSPORT", "streamable-http")  # Default to HTTP

    logger.info("Starting Service Hub MCP Server")
    logger.info(f"Transport: {transport}")
    logger.info("Available tools: YouTube transcripts (via core library)")
    logger.info("Future tools: RSS, database, file operations")

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
# Run with: uvicorn mcp.server:app --host 0.0.0.0 --port 8001
app = mcp.streamable_http_app()
