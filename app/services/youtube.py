"""YouTube transcript fetching service."""

import os
import re
from pathlib import Path
from typing import Any, Literal

from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import (
    InvalidVideoId,
    NoTranscriptFound,
    TranscriptsDisabled,
    VideoUnavailable,
)

from app.core.cache import TTLCache


class YouTubeService:
    """Service for fetching YouTube transcripts with caching support."""

    def __init__(self, cache: TTLCache | None = None):
        """Initialize YouTube service.

        Args:
            cache: Optional TTL cache for caching transcript results
        """
        self.cache = cache

    @staticmethod
    def extract_video_id(url_or_id: str) -> str | None:
        """Extract video ID from YouTube URL or return as-is if already an ID.

        Args:
            url_or_id: YouTube URL or video ID

        Returns:
            11-character video ID or None if invalid
        """
        if len(url_or_id) > 500:
            return None

        patterns = [
            r"(?:v=|\/)([0-9A-Za-z_-]{11}).*",
            r"(?:embed\/)([0-9A-Za-z_-]{11})",
            r"^([0-9A-Za-z_-]{11})$",
        ]

        for pattern in patterns:
            match = re.search(pattern, url_or_id)
            if match and re.match(r"^[0-9A-Za-z_-]{11}$", match.group(1)):
                # Sanitize for logging
                return re.sub(r"[^\w-]", "", match.group(1))

        return None

    @staticmethod
    def create_api_client() -> YouTubeTranscriptApi:
        """Create YouTubeTranscriptApi instance with optional env configuration.

        Returns:
            Configured YouTubeTranscriptApi instance
        """
        kwargs: dict[str, Any] = {}

        proxy_http = os.environ.get("YOUTUBE_PROXY_HTTP")
        proxy_https = os.environ.get("YOUTUBE_PROXY_HTTPS")
        if proxy_http or proxy_https:
            from youtube_transcript_api.proxies import GenericProxyConfig

            kwargs["proxy_config"] = GenericProxyConfig(
                http_url=proxy_http, https_url=proxy_https or proxy_http
            )

        return YouTubeTranscriptApi(**kwargs)

    @staticmethod
    def _format_timestamp_srt(seconds: float) -> str:
        """Format seconds to SRT timestamp (HH:MM:SS,mmm)."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

    @staticmethod
    def _format_timestamp_vtt(seconds: float) -> str:
        """Format seconds to WebVTT timestamp (HH:MM:SS.mmm)."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d}.{millis:03d}"

    @staticmethod
    def format_transcript(
        transcript_data: Any,
        format_type: Literal["plain", "structured", "srt", "vtt"] = "plain",
    ) -> str | dict[str, Any]:
        """Format transcript data according to requested format.

        Args:
            transcript_data: Raw transcript data from YouTube API
            format_type: Desired output format

        Returns:
            Formatted transcript as string or dict
        """
        if format_type == "plain":
            return "\n".join(entry["text"] for entry in transcript_data)

        elif format_type == "structured":
            return {
                "entries": [
                    {
                        "text": entry["text"],
                        "start": entry["start"],
                        "duration": entry["duration"],
                    }
                    for entry in transcript_data
                ]
            }

        elif format_type == "srt":
            # SRT subtitle format
            srt_output = []
            for idx, entry in enumerate(transcript_data, 1):
                start = YouTubeService._format_timestamp_srt(entry["start"])
                end = YouTubeService._format_timestamp_srt(
                    entry["start"] + entry["duration"]
                )
                srt_output.append(f"{idx}\n{start} --> {end}\n{entry['text']}\n")
            return "\n".join(srt_output)

        elif format_type == "vtt":
            # WebVTT format
            vtt_output = ["WEBVTT\n"]
            for entry in transcript_data:
                start = YouTubeService._format_timestamp_vtt(entry["start"])
                end = YouTubeService._format_timestamp_vtt(
                    entry["start"] + entry["duration"]
                )
                vtt_output.append(f"{start} --> {end}\n{entry['text']}\n")
            return "\n".join(vtt_output)

        return "\n".join(entry["text"] for entry in transcript_data)

    def get_transcript(
        self,
        video_url_or_id: str,
        languages: list[str] | None = None,
        format_type: Literal["plain", "structured", "srt", "vtt"] = "plain",
    ) -> dict[str, Any]:
        """Fetch YouTube video transcript with caching.

        Args:
            video_url_or_id: YouTube URL or 11-character video ID
            languages: Preferred languages in order (default: ["en"])
            format_type: Output format (plain, structured, srt, vtt)

        Returns:
            Dictionary with transcript data and metadata
        """
        video_id = self.extract_video_id(video_url_or_id)
        if not video_id:
            return {
                "success": False,
                "error": "INVALID_VIDEO_ID",
                "message": "Could not extract valid YouTube video ID from input",
            }

        languages = languages or ["en"]

        # Generate cache key (defined outside conditional for later use)
        cache_key = f"transcript:{video_id}:{format_type}:{','.join(languages)}"

        # Check cache if available
        if self.cache:
            cached = self.cache.get(cache_key)
            if cached:
                return {**cached, "cached": True}

        try:
            api = self.create_api_client()
            # Use the new 1.2.3 API: instance.fetch(video_id, languages)
            transcript_data = api.fetch(video_id, languages=languages)

            # Format according to requested type
            formatted = self.format_transcript(transcript_data, format_type)

            result = {
                "success": True,
                "video_id": video_id,
                "transcript": formatted,
                "language": transcript_data.language_code
                if hasattr(transcript_data, "language_code")
                else "unknown",
                "is_generated": transcript_data.is_generated
                if hasattr(transcript_data, "is_generated")
                else False,
                "format": format_type,
                "cached": False,
            }

            # Cache successful results
            if self.cache:
                self.cache.set(cache_key, result)

            return result

        except TranscriptsDisabled:
            return {
                "success": False,
                "video_id": video_id,
                "error": "TRANSCRIPTS_DISABLED",
                "message": "Transcripts are disabled for this video",
            }

        except NoTranscriptFound:
            return {
                "success": False,
                "video_id": video_id,
                "error": "NO_TRANSCRIPT_FOUND",
                "message": f"No transcript found for languages: {', '.join(languages)}",
            }

        except VideoUnavailable:
            return {
                "success": False,
                "video_id": video_id,
                "error": "VIDEO_UNAVAILABLE",
                "message": "Video is unavailable or private",
            }

        except InvalidVideoId:
            return {
                "success": False,
                "video_id": video_id,
                "error": "INVALID_VIDEO_ID",
                "message": "Invalid YouTube video ID",
            }

        except Exception as e:
            return {
                "success": False,
                "video_id": video_id,
                "error": "UNKNOWN_ERROR",
                "message": f"Unexpected error: {type(e).__name__}: {str(e)}",
            }

    def list_transcript_languages(self, video_url_or_id: str) -> dict[str, Any]:
        """List all available transcript languages for a video.

        Args:
            video_url_or_id: YouTube URL or video ID

        Returns:
            Dictionary with available languages or error information
        """
        video_id = self.extract_video_id(video_url_or_id)
        if not video_id:
            return {
                "success": False,
                "error": "INVALID_VIDEO_ID",
                "message": "Could not extract valid YouTube video ID from input",
            }

        try:
            api = self.create_api_client()
            transcript_list = api.list(video_id)

            languages = []
            for transcript in transcript_list:
                languages.append(
                    {
                        "code": transcript.language_code,
                        "name": transcript.language,
                        "is_generated": transcript.is_generated,
                        "is_translatable": transcript.is_translatable,
                    }
                )

            return {"success": True, "video_id": video_id, "languages": languages}

        except (
            TranscriptsDisabled,
            NoTranscriptFound,
            VideoUnavailable,
            InvalidVideoId,
        ) as e:
            return {
                "success": False,
                "video_id": video_id,
                "error": type(e).__name__.upper(),
                "message": str(e),
            }

        except Exception as e:
            return {
                "success": False,
                "video_id": video_id,
                "error": "UNKNOWN_ERROR",
                "message": f"Unexpected error: {type(e).__name__}: {str(e)}",
            }
