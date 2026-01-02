"""Tests for CLI commands."""

from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from cli.youtube import app
from lib.youtube.models import LanguageInfo, LanguagesResponse, TranscriptResponse

runner = CliRunner()


class TestGetTranscriptCommand:
    """Test get-transcript CLI command."""

    @patch("cli.youtube.TranscriptService")
    def test_get_transcript_success(self, mock_service_class):
        """Test successful transcript fetch."""
        mock_service = MagicMock()
        mock_service_class.return_value = mock_service
        mock_service.get_transcript.return_value = TranscriptResponse(
            success=True,
            video_id="dQw4w9WgXcQ",
            transcript="Hello World",
            format="plain",
            cached=False,
        )

        result = runner.invoke(app, ["get-transcript", "dQw4w9WgXcQ"])

        assert result.exit_code == 0
        assert "Hello World" in result.stdout

    @patch("cli.youtube.TranscriptService")
    def test_get_transcript_json_format(self, mock_service_class):
        """Test transcript fetch with JSON format."""
        mock_service = MagicMock()
        mock_service_class.return_value = mock_service
        mock_service.get_transcript.return_value = TranscriptResponse(
            success=True,
            video_id="dQw4w9WgXcQ",
            transcript={"entries": [{"text": "Hello"}]},
            format="structured",
            cached=False,
        )

        result = runner.invoke(app, ["get-transcript", "dQw4w9WgXcQ", "-f", "json"])

        assert result.exit_code == 0
        assert "entries" in result.stdout

    @patch("cli.youtube.TranscriptService")
    def test_get_transcript_with_language(self, mock_service_class):
        """Test transcript fetch with specific language."""
        mock_service = MagicMock()
        mock_service_class.return_value = mock_service
        mock_service.get_transcript.return_value = TranscriptResponse(
            success=True,
            video_id="dQw4w9WgXcQ",
            transcript={"entries": [{"text": "Hello"}]},
            format="structured",
            cached=False,
        )

        result = runner.invoke(app, ["get-transcript", "dQw4w9WgXcQ", "-l", "es"])

        assert result.exit_code == 0
        mock_service.get_transcript.assert_called_once()
        # Check that languages parameter was passed
        call_args = mock_service.get_transcript.call_args
        assert "es" in call_args.kwargs["languages"]

    @patch("cli.youtube.TranscriptService")
    def test_get_transcript_multiple_languages(self, mock_service_class):
        """Test transcript fetch with multiple fallback languages."""
        mock_service = MagicMock()
        mock_service_class.return_value = mock_service
        mock_service.get_transcript.return_value = TranscriptResponse(
            success=True,
            video_id="dQw4w9WgXcQ",
            transcript={"entries": [{"text": "Hello"}]},
            format="structured",
            cached=False,
        )

        result = runner.invoke(
            app, ["get-transcript", "dQw4w9WgXcQ", "-l", "en", "-l", "es"]
        )

        assert result.exit_code == 0
        call_args = mock_service.get_transcript.call_args
        assert "en" in call_args.kwargs["languages"]
        assert "es" in call_args.kwargs["languages"]

    @patch("cli.youtube.TranscriptService")
    def test_get_transcript_invalid_video_id(self, mock_service_class):
        """Test transcript fetch with invalid video ID."""
        mock_service = MagicMock()
        mock_service_class.return_value = mock_service
        mock_service.get_transcript.return_value = TranscriptResponse(
            success=False,
            video_id="invalid",
            error="INVALID_VIDEO_ID",
            message="Could not extract valid YouTube video ID from input",
        )

        result = runner.invoke(app, ["get-transcript", "invalid"])

        assert result.exit_code == 2  # Invalid video ID exit code
        assert "Error" in result.stdout

    @patch("cli.youtube.TranscriptService")
    def test_get_transcript_not_found(self, mock_service_class):
        """Test transcript fetch when transcript not found."""
        mock_service = MagicMock()
        mock_service_class.return_value = mock_service
        mock_service.get_transcript.return_value = TranscriptResponse(
            success=False,
            video_id="dQw4w9WgXcQ",
            error="NO_TRANSCRIPT_FOUND",
            message="No transcript found",
        )

        result = runner.invoke(app, ["get-transcript", "dQw4w9WgXcQ"])

        assert result.exit_code == 3  # No transcript exit code

    @patch("cli.youtube.TranscriptService")
    @patch("cli.youtube.Path")
    def test_get_transcript_output_to_file(self, mock_path_class, mock_service_class):
        """Test saving transcript to file."""
        mock_service = MagicMock()
        mock_service_class.return_value = mock_service
        mock_service.get_transcript.return_value = TranscriptResponse(
            success=True,
            video_id="dQw4w9WgXcQ",
            transcript="Hello World",
            format="plain",
            cached=False,
        )

        mock_path = MagicMock()
        mock_path_class.return_value = mock_path

        result = runner.invoke(
            app, ["get-transcript", "dQw4w9WgXcQ", "-o", "output.txt"]
        )

        assert result.exit_code == 0
        # Verify Path was created and write_text was called
        mock_path_class.assert_called_once_with("output.txt")
        mock_path.write_text.assert_called_once_with("Hello World")


class TestListLanguagesCommand:
    """Test list-languages CLI command."""

    @patch("cli.youtube.TranscriptService")
    def test_list_languages_success(self, mock_service_class):
        """Test successful language listing."""
        mock_service = MagicMock()
        mock_service_class.return_value = mock_service
        mock_service.list_languages.return_value = LanguagesResponse(
            success=True,
            video_id="dQw4w9WgXcQ",
            languages=[
                LanguageInfo(
                    code="en", name="English", is_generated=False, is_translatable=True
                ),
                LanguageInfo(
                    code="es", name="Spanish", is_generated=True, is_translatable=False
                ),
            ],
        )

        result = runner.invoke(app, ["list-languages", "dQw4w9WgXcQ"])

        assert result.exit_code == 0
        assert "English" in result.stdout
        assert "Spanish" in result.stdout

    @patch("cli.youtube.TranscriptService")
    def test_list_languages_json_format(self, mock_service_class):
        """Test language listing with JSON output."""
        mock_service = MagicMock()
        mock_service_class.return_value = mock_service
        mock_service.list_languages.return_value = LanguagesResponse(
            success=True,
            video_id="dQw4w9WgXcQ",
            languages=[
                LanguageInfo(
                    code="en", name="English", is_generated=False, is_translatable=True
                ),
            ],
        )

        result = runner.invoke(app, ["list-languages", "dQw4w9WgXcQ", "--json"])

        assert result.exit_code == 0
        assert "languages" in result.stdout
        assert "en" in result.stdout

    @patch("cli.youtube.TranscriptService")
    def test_list_languages_invalid_video_id(self, mock_service_class):
        """Test language listing with invalid video ID."""
        mock_service = MagicMock()
        mock_service_class.return_value = mock_service
        mock_service.list_languages.return_value = LanguagesResponse(
            success=False,
            video_id="invalid",
            error="INVALID_VIDEO_ID",
            message="Could not extract valid YouTube video ID from input",
        )

        result = runner.invoke(app, ["list-languages", "invalid"])

        assert result.exit_code == 2  # Invalid video ID exit code


class TestVersionCommand:
    """Test version CLI command."""

    def test_version_command(self):
        """Test version command output."""
        result = runner.invoke(app, ["version"])

        assert result.exit_code == 0
        assert "YouTube Transcript CLI" in result.stdout
        assert "1.0.0" in result.stdout


class TestCLIHelp:
    """Test CLI help messages."""

    def test_main_help(self):
        """Test main help message."""
        result = runner.invoke(app, ["--help"])

        assert result.exit_code == 0
        assert "YouTube transcript CLI tool" in result.stdout
        assert "get-transcript" in result.stdout
        assert "list-languages" in result.stdout
        assert "version" in result.stdout

    def test_get_transcript_help(self):
        """Test get-transcript help message."""
        result = runner.invoke(app, ["get-transcript", "--help"])

        assert result.exit_code == 0
        assert "Fetch YouTube video transcript" in result.stdout
        assert "--lang" in result.stdout or "-l" in result.stdout
        assert "--format" in result.stdout or "-f" in result.stdout

    def test_list_languages_help(self):
        """Test list-languages help message."""
        result = runner.invoke(app, ["list-languages", "--help"])

        assert result.exit_code == 0
        assert "List available transcript languages" in result.stdout
