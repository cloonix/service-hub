"""Transcript formatting utilities."""

from typing import Any


def _get_field(entry: Any, field: str) -> Any:
    """Get field from entry (dict or object).

    Args:
        entry: Dictionary or object with attributes
        field: Field name to retrieve

    Returns:
        Field value
    """
    return entry[field] if isinstance(entry, dict) else getattr(entry, field)


def format_plain(transcript_data: Any) -> str:
    """Format transcript as plain text.

    Args:
        transcript_data: Raw transcript data from YouTube API

    Returns:
        Plain text transcript (one line per entry)
    """
    return "\n".join(_get_field(entry, "text") for entry in transcript_data)


def format_structured(transcript_data: Any) -> dict[str, Any]:
    """Format transcript as structured JSON with timestamps.

    Args:
        transcript_data: Raw transcript data from YouTube API

    Returns:
        Dictionary with structured entries
    """
    return {
        "entries": [
            {
                "text": _get_field(entry, "text"),
                "start": _get_field(entry, "start"),
                "duration": _get_field(entry, "duration"),
            }
            for entry in transcript_data
        ]
    }
