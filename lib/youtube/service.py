"""YouTube transcript service - core business logic."""

import os
import re
from typing import Any

from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import (
    InvalidVideoId,
    NoTranscriptFound,
    TranscriptsDisabled,
    VideoUnavailable,
)

from lib.youtube.cache import CacheProtocol
from lib.youtube.formatters import (
    format_plain,
    format_srt,
    format_structured,
    format_vtt,
)
from lib.youtube.models import FormatType, LanguagesResponse, TranscriptResponse


class TranscriptService:
    """Service for fetching YouTube transcripts.

    This is the core business logic for YouTube transcript operations.
    It can be used by APIs, CLIs, MCP servers, or any other interface.
    """

    def __init__(self, cache: CacheProtocol | None = None):
        """Initialize transcript service.

        Args:
            cache: Optional cache implementation (must implement CacheProtocol)
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

    def format_transcript(
        self, transcript_data: Any, format_type: FormatType | str
    ) -> str | dict[str, Any]:
        """Format transcript data according to requested format.

        Args:
            transcript_data: Raw transcript data from YouTube API
            format_type: Desired output format

        Returns:
            Formatted transcript as string or dict
        """
        # Convert string to enum if needed
        if isinstance(format_type, str):
            format_type = FormatType(format_type)

        if format_type == FormatType.PLAIN:
            return format_plain(transcript_data)
        elif format_type == FormatType.STRUCTURED:
            return format_structured(transcript_data)
        elif format_type == FormatType.SRT:
            return format_srt(transcript_data)
        elif format_type == FormatType.VTT:
            return format_vtt(transcript_data)
        else:
            return format_plain(transcript_data)

    def get_transcript(
        self,
        video_url_or_id: str,
        languages: list[str] | None = None,
        format_type: FormatType | str = FormatType.PLAIN,
    ) -> TranscriptResponse:
        """Fetch YouTube video transcript with caching.

        Args:
            video_url_or_id: YouTube URL or 11-character video ID
            languages: Preferred languages in order (default: ["en"])
            format_type: Output format (plain, structured, srt, vtt)

        Returns:
            TranscriptResponse with transcript data and metadata
        """
        video_id = self.extract_video_id(video_url_or_id)
        if not video_id:
            return TranscriptResponse(
                success=False,
                error="INVALID_VIDEO_ID",
                message="Could not extract valid YouTube video ID from input",
            )

        languages = languages or ["en"]

        # Convert string to enum if needed
        if isinstance(format_type, str):
            format_type = FormatType(format_type)

        # Generate cache key
        cache_key = f"transcript:{video_id}:{format_type.value}:{','.join(languages)}"

        # Check cache if available
        if self.cache:
            cached = self.cache.get(cache_key)
            if cached:
                return TranscriptResponse(**{**cached, "cached": True})

        try:
            api = self.create_api_client()
            # Use the new 1.2.3 API: instance.fetch(video_id, languages)
            transcript_data = api.fetch(video_id, languages=languages)

            # Format according to requested type
            formatted = self.format_transcript(transcript_data, format_type)

            result = TranscriptResponse(
                success=True,
                video_id=video_id,
                transcript=formatted,
                language=transcript_data.language_code
                if hasattr(transcript_data, "language_code")
                else "unknown",
                is_generated=transcript_data.is_generated
                if hasattr(transcript_data, "is_generated")
                else False,
                format=format_type.value,
                cached=False,
            )

            # Cache successful results
            if self.cache:
                self.cache.set(cache_key, result.model_dump(exclude={"cached"}))

            return result

        except TranscriptsDisabled:
            return TranscriptResponse(
                success=False,
                video_id=video_id,
                error="TRANSCRIPTS_DISABLED",
                message="Transcripts are disabled for this video",
            )

        except NoTranscriptFound:
            return TranscriptResponse(
                success=False,
                video_id=video_id,
                error="NO_TRANSCRIPT_FOUND",
                message=f"No transcript found for languages: {', '.join(languages)}",
            )

        except VideoUnavailable:
            return TranscriptResponse(
                success=False,
                video_id=video_id,
                error="VIDEO_UNAVAILABLE",
                message="Video is unavailable or private",
            )

        except InvalidVideoId:
            return TranscriptResponse(
                success=False,
                video_id=video_id,
                error="INVALID_VIDEO_ID",
                message="Invalid YouTube video ID",
            )

        except Exception as e:
            return TranscriptResponse(
                success=False,
                video_id=video_id,
                error="UNKNOWN_ERROR",
                message=f"Unexpected error: {type(e).__name__}: {str(e)}",
            )

    def list_languages(self, video_url_or_id: str) -> LanguagesResponse:
        """List all available transcript languages for a video.

        Args:
            video_url_or_id: YouTube URL or video ID

        Returns:
            LanguagesResponse with available languages or error information
        """
        video_id = self.extract_video_id(video_url_or_id)
        if not video_id:
            return LanguagesResponse(
                success=False,
                error="INVALID_VIDEO_ID",
                message="Could not extract valid YouTube video ID from input",
            )

        try:
            api = self.create_api_client()
            transcript_list = api.list(video_id)

            from lib.youtube.models import LanguageInfo

            languages = []
            for transcript in transcript_list:
                languages.append(
                    LanguageInfo(
                        code=transcript.language_code,
                        name=transcript.language,
                        is_generated=transcript.is_generated,
                        is_translatable=transcript.is_translatable,
                    )
                )

            return LanguagesResponse(
                success=True, video_id=video_id, languages=languages
            )

        except (
            TranscriptsDisabled,
            NoTranscriptFound,
            VideoUnavailable,
            InvalidVideoId,
        ) as e:
            return LanguagesResponse(
                success=False,
                video_id=video_id,
                error=type(e).__name__.upper(),
                message=str(e),
            )

        except Exception as e:
            return LanguagesResponse(
                success=False,
                video_id=video_id,
                error="UNKNOWN_ERROR",
                message=f"Unexpected error: {type(e).__name__}: {str(e)}",
            )
