"""YouTube transcript library.

A reusable library for fetching YouTube video transcripts in multiple formats.
Can be used by API servers, MCP tools, CLI applications, and more.
"""

from lib.youtube.exceptions import (
    InvalidVideoIdError,
    TranscriptError,
    TranscriptNotFoundError,
    VideoUnavailableError,
)
from lib.youtube.models import (
    FormatType,
    LanguageInfo,
    LanguagesResponse,
    TranscriptRequest,
    TranscriptResponse,
)
from lib.youtube.service import TranscriptService

__all__ = [
    # Service
    "TranscriptService",
    # Models
    "TranscriptRequest",
    "TranscriptResponse",
    "LanguagesResponse",
    "LanguageInfo",
    "FormatType",
    # Exceptions
    "TranscriptError",
    "InvalidVideoIdError",
    "TranscriptNotFoundError",
    "VideoUnavailableError",
]
