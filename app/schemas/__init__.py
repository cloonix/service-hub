"""Pydantic schemas for API requests and responses."""

from app.schemas.common import ErrorResponse, SuccessResponse

# YouTube schemas are re-exported from lib.youtube.models
from lib.youtube.models import (
    FormatType,
    LanguageInfo,
    LanguagesResponse,
    TranscriptRequest,
    TranscriptResponse,
)

__all__ = [
    # Common
    "SuccessResponse",
    "ErrorResponse",
    # YouTube (re-exported from library)
    "TranscriptRequest",
    "TranscriptResponse",
    "LanguagesResponse",
    "LanguageInfo",
    "FormatType",
]
