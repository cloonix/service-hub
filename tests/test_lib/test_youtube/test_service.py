"""Tests for YouTube transcript service."""

from unittest.mock import MagicMock, patch

import pytest
from youtube_transcript_api._errors import (
    InvalidVideoId,
    NoTranscriptFound,
    TranscriptsDisabled,
    VideoUnavailable,
)

from lib.youtube.models import FormatType
from lib.youtube.service import TranscriptService


class TestVideoIdExtraction:
    """Test video ID extraction from various formats."""

    def test_extract_from_standard_url(self):
        """Test extraction from standard YouTube URL."""
        service = TranscriptService()
        video_id = service.extract_video_id(
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        )
        assert video_id == "dQw4w9WgXcQ"

    def test_extract_from_short_url(self):
        """Test extraction from short youtu.be URL."""
        service = TranscriptService()
        video_id = service.extract_video_id("https://youtu.be/dQw4w9WgXcQ")
        assert video_id == "dQw4w9WgXcQ"

    def test_extract_from_embed_url(self):
        """Test extraction from embed URL."""
        service = TranscriptService()
        video_id = service.extract_video_id("https://www.youtube.com/embed/dQw4w9WgXcQ")
        assert video_id == "dQw4w9WgXcQ"

    def test_extract_from_bare_id(self):
        """Test extraction from bare video ID."""
        service = TranscriptService()
        video_id = service.extract_video_id("dQw4w9WgXcQ")
        assert video_id == "dQw4w9WgXcQ"

    def test_extract_invalid_returns_none(self):
        """Test that invalid input returns None."""
        service = TranscriptService()
        assert service.extract_video_id("invalid") is None
        assert service.extract_video_id("") is None
        assert service.extract_video_id("x" * 600) is None


class TestGetTranscript:
    """Test transcript fetching."""

    @patch("lib.youtube.service.YouTubeTranscriptApi")
    def test_get_transcript_success(self, mock_api_class):
        """Test successful transcript fetch."""
        # Setup mock - use the new 1.2.3 API
        mock_api = MagicMock()
        mock_api_class.return_value = mock_api

        # Mock the transcript data with required attributes
        mock_transcript = MagicMock()
        mock_transcript.__iter__.return_value = iter(
            [
                {"text": "Hello", "start": 0.0, "duration": 1.0},
                {"text": "World", "start": 1.0, "duration": 1.0},
            ]
        )
        mock_transcript.language_code = "en"
        mock_transcript.is_generated = False

        mock_api.fetch.return_value = mock_transcript

        service = TranscriptService()
        result = service.get_transcript("dQw4w9WgXcQ", languages=["en"])

        assert result.success is True
        assert result.video_id == "dQw4w9WgXcQ"
        assert result.format == "plain"
        assert result.transcript is not None
        assert isinstance(result.transcript, str)
        assert "Hello" in result.transcript
        assert "World" in result.transcript

    @patch("lib.youtube.service.YouTubeTranscriptApi")
    def test_get_transcript_json_format(self, mock_api_class):
        """Test transcript fetch with JSON format."""
        mock_api = MagicMock()
        mock_api_class.return_value = mock_api

        # Mock the transcript data with required attributes
        mock_transcript = MagicMock()
        mock_transcript.__iter__.return_value = iter(
            [
                {"text": "Hello", "start": 0.0, "duration": 1.0},
            ]
        )
        mock_transcript.language_code = "en"
        mock_transcript.is_generated = False

        mock_api.fetch.return_value = mock_transcript

        service = TranscriptService()
        result = service.get_transcript(
            "dQw4w9WgXcQ", languages=["en"], format_type=FormatType.STRUCTURED
        )

        assert result.success is True
        assert result.format == "structured"
        assert isinstance(result.transcript, dict)

    @patch("lib.youtube.service.YouTubeTranscriptApi")
    def test_get_transcript_with_cache(self, mock_api_class):
        """Test transcript caching."""
        mock_cache = MagicMock()
        mock_cache.get.return_value = None  # Cache miss

        mock_api = MagicMock()
        mock_api_class.return_value = mock_api

        # Mock the transcript data with required attributes
        mock_transcript = MagicMock()
        mock_transcript.__iter__.return_value = iter(
            [
                {"text": "Hello", "start": 0.0, "duration": 1.0},
            ]
        )
        mock_transcript.language_code = "en"
        mock_transcript.is_generated = False

        mock_api.fetch.return_value = mock_transcript

        service = TranscriptService(cache=mock_cache)
        result = service.get_transcript("dQw4w9WgXcQ")

        assert result.success is True
        # Verify cache was queried and set
        mock_cache.get.assert_called_once()
        mock_cache.set.assert_called_once()

    def test_get_transcript_invalid_video_id(self):
        """Test transcript fetch with invalid video ID."""
        service = TranscriptService()
        result = service.get_transcript("invalid")

        assert result.success is False
        assert result.error == "INVALID_VIDEO_ID"

    @patch("lib.youtube.service.YouTubeTranscriptApi")
    def test_get_transcript_transcripts_disabled(self, mock_api_class):
        """Test handling of transcripts disabled error."""
        mock_api = MagicMock()
        mock_api_class.return_value = mock_api
        mock_api.fetch.side_effect = TranscriptsDisabled("video_id")

        service = TranscriptService()
        result = service.get_transcript("dQw4w9WgXcQ")

        assert result.success is False
        assert result.error == "TRANSCRIPTS_DISABLED"

    @patch("lib.youtube.service.YouTubeTranscriptApi")
    def test_get_transcript_not_found(self, mock_api_class):
        """Test handling of transcript not found error."""
        mock_api = MagicMock()
        mock_api_class.return_value = mock_api
        mock_api.fetch.side_effect = NoTranscriptFound("video_id", ["en"], None)

        service = TranscriptService()
        result = service.get_transcript("dQw4w9WgXcQ")

        assert result.success is False
        assert result.error == "NO_TRANSCRIPT_FOUND"

    @patch("lib.youtube.service.YouTubeTranscriptApi")
    def test_get_transcript_video_unavailable(self, mock_api_class):
        """Test handling of video unavailable error."""
        mock_api = MagicMock()
        mock_api_class.return_value = mock_api
        mock_api.fetch.side_effect = VideoUnavailable("video_id")

        service = TranscriptService()
        result = service.get_transcript("dQw4w9WgXcQ")

        assert result.success is False
        assert result.error == "VIDEO_UNAVAILABLE"


class TestListLanguages:
    """Test language listing."""

    @patch("lib.youtube.service.YouTubeTranscriptApi")
    def test_list_languages_success(self, mock_api_class):
        """Test successful language listing."""
        mock_api = MagicMock()
        mock_api_class.return_value = mock_api

        # Mock transcript list
        mock_transcript = MagicMock()
        mock_transcript.language_code = "en"
        mock_transcript.language = "English"
        mock_transcript.is_generated = False
        mock_transcript.is_translatable = True

        mock_api.list.return_value = [mock_transcript]

        service = TranscriptService()
        result = service.list_languages("dQw4w9WgXcQ")

        assert result.success is True
        assert result.languages is not None
        assert len(result.languages) == 1
        assert result.languages[0].code == "en"
        assert result.languages[0].name == "English"

    def test_list_languages_invalid_video_id(self):
        """Test language list with invalid video ID."""
        service = TranscriptService()
        result = service.list_languages("invalid")

        assert result.success is False
        assert result.error == "INVALID_VIDEO_ID"

    @patch("lib.youtube.service.YouTubeTranscriptApi")
    def test_list_languages_error_handling(self, mock_api_class):
        """Test error handling in language listing."""
        mock_api = MagicMock()
        mock_api_class.return_value = mock_api
        mock_api.list.side_effect = VideoUnavailable("video_id")

        service = TranscriptService()
        result = service.list_languages("dQw4w9WgXcQ")

        assert result.success is False
        assert result.error == "VIDEO_UNAVAILABLE"


class TestErrorCodeGeneration:
    """Test error code generation helper."""

    def test_error_code_from_camel_case(self):
        """Test error code generation from CamelCase exception."""
        service = TranscriptService()

        # Test various exception types
        error_code = service._error_code_from_exception(InvalidVideoId("test"))
        assert error_code == "INVALID_VIDEO_ID"

        error_code = service._error_code_from_exception(TranscriptsDisabled("test"))
        assert error_code == "TRANSCRIPTS_DISABLED"

        error_code = service._error_code_from_exception(
            NoTranscriptFound("test", [], None)
        )
        assert error_code == "NO_TRANSCRIPT_FOUND"
