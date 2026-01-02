"""Transcript formatting utilities."""

from typing import Any


def format_timestamp_srt(seconds: float) -> str:
    """Format seconds to SRT timestamp (HH:MM:SS,mmm).

    Args:
        seconds: Time in seconds

    Returns:
        SRT formatted timestamp
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def format_timestamp_vtt(seconds: float) -> str:
    """Format seconds to WebVTT timestamp (HH:MM:SS.mmm).

    Args:
        seconds: Time in seconds

    Returns:
        WebVTT formatted timestamp
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}.{millis:03d}"


def format_plain(transcript_data: Any) -> str:
    """Format transcript as plain text.

    Args:
        transcript_data: Raw transcript data from YouTube API

    Returns:
        Plain text transcript (one line per entry)
    """
    return "\n".join(entry.text for entry in transcript_data)


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
                "text": entry.text,
                "start": entry.start,
                "duration": entry.duration,
            }
            for entry in transcript_data
        ]
    }


def format_srt(transcript_data: Any) -> str:
    """Format transcript as SRT subtitle file.

    Args:
        transcript_data: Raw transcript data from YouTube API

    Returns:
        SRT formatted transcript
    """
    srt_output = []
    for idx, entry in enumerate(transcript_data, 1):
        start = format_timestamp_srt(entry.start)
        end = format_timestamp_srt(entry.start + entry.duration)
        srt_output.append(f"{idx}\n{start} --> {end}\n{entry.text}\n")
    return "\n".join(srt_output)


def format_vtt(transcript_data: Any) -> str:
    """Format transcript as WebVTT subtitle file.

    Args:
        transcript_data: Raw transcript data from YouTube API

    Returns:
        WebVTT formatted transcript
    """
    vtt_output = ["WEBVTT\n"]
    for entry in transcript_data:
        start = format_timestamp_vtt(entry.start)
        end = format_timestamp_vtt(entry.start + entry.duration)
        vtt_output.append(f"{start} --> {end}\n{entry.text}\n")
    return "\n".join(vtt_output)
