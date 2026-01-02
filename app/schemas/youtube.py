"""Pydantic schemas for YouTube transcript API.

This module re-exports models from the core library for backward compatibility.
"""

from lib.youtube.models import (
    FormatType,
    LanguageInfo,
    LanguagesResponse,
    StructuredTranscript,
    TranscriptEntry,
    TranscriptRequest,
    TranscriptResponse,
)

__all__ = [
    "FormatType",
    "TranscriptRequest",
    "TranscriptEntry",
    "StructuredTranscript",
    "TranscriptResponse",
    "LanguageInfo",
    "LanguagesResponse",
]
