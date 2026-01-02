"""Custom exceptions for YouTube transcript library."""


class TranscriptError(Exception):
    """Base exception for YouTube transcript errors."""

    pass


class InvalidVideoIdError(TranscriptError):
    """Raised when video ID is invalid or cannot be extracted."""

    pass


class TranscriptNotFoundError(TranscriptError):
    """Raised when no transcript is found for the requested languages."""

    pass


class VideoUnavailableError(TranscriptError):
    """Raised when the video is unavailable or private."""

    pass
