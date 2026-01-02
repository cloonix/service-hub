"""Pydantic schemas for YouTube transcript API."""

from typing import Any, Literal

from pydantic import BaseModel, Field


class TranscriptRequest(BaseModel):
    """Request schema for fetching YouTube transcripts."""

    video_url_or_id: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="YouTube URL or 11-character video ID",
    )
    languages: list[str] | None = Field(
        default=None,
        max_length=10,
        description="Preferred languages in order of preference",
    )
    format_type: Literal["plain", "structured", "srt", "vtt"] = Field(
        default="plain", description="Output format for the transcript"
    )


class TranscriptEntry(BaseModel):
    """Single transcript entry with timing information."""

    text: str
    start: float
    duration: float


class StructuredTranscript(BaseModel):
    """Structured transcript with individual entries."""

    entries: list[TranscriptEntry]


class TranscriptResponse(BaseModel):
    """Response schema for transcript fetching."""

    success: bool
    video_id: str | None = None
    transcript: str | dict[str, Any] | None = None
    language: str | None = None
    is_generated: bool | None = None
    format: str | None = None
    cached: bool = False
    error: str | None = None
    message: str | None = None


class LanguageInfo(BaseModel):
    """Information about an available transcript language."""

    code: str = Field(..., description="Language code (e.g., 'en', 'es')")
    name: str = Field(..., description="Language name")
    is_generated: bool = Field(..., description="Whether this is auto-generated")
    is_translatable: bool = Field(..., description="Whether this can be translated")


class LanguagesResponse(BaseModel):
    """Response schema for listing available languages."""

    success: bool
    video_id: str | None = None
    languages: list[LanguageInfo] | None = None
    error: str | None = None
    message: str | None = None
