"""Tests for YouTube transcript formatters."""

from lib.youtube.formatters import (
    format_plain,
    format_structured,
)


class TestPlainFormatter:
    """Test plain text formatter."""

    def test_format_plain_simple(self):
        """Test basic plain text formatting."""
        transcript = [
            {"text": "Hello", "start": 0.0, "duration": 1.0},
            {"text": "World", "start": 1.0, "duration": 1.0},
        ]

        result = format_plain(transcript)

        assert "Hello" in result
        assert "World" in result
        assert result == "Hello\nWorld"

    def test_format_plain_empty(self):
        """Test plain text with empty transcript."""
        result = format_plain([])
        assert result == ""

    def test_format_plain_single_entry(self):
        """Test plain text with single entry."""
        transcript = [{"text": "Single line", "start": 0.0, "duration": 1.0}]
        result = format_plain(transcript)
        assert result == "Single line"


class TestStructuredFormatter:
    """Test structured (JSON) formatter."""

    def test_format_structured(self):
        """Test structured JSON formatting."""
        transcript = [
            {"text": "Hello", "start": 0.0, "duration": 1.0},
            {"text": "World", "start": 1.0, "duration": 1.0},
        ]

        result = format_structured(transcript)

        assert isinstance(result, dict)
        assert "entries" in result
        assert len(result["entries"]) == 2
        assert result["entries"][0]["text"] == "Hello"
        assert result["entries"][0]["start"] == 0.0
        assert result["entries"][1]["text"] == "World"

    def test_format_structured_preserves_metadata(self):
        """Test that structured format preserves all metadata."""
        transcript = [
            {"text": "Test", "start": 5.5, "duration": 2.3},
        ]

        result = format_structured(transcript)

        assert result["entries"][0]["start"] == 5.5
        assert result["entries"][0]["duration"] == 2.3

    def test_format_structured_empty(self):
        """Test structured format with empty transcript."""
        result = format_structured([])
        assert result == {"entries": []}


class TestFormatterEdgeCases:
    """Test edge cases across all formatters."""

    def test_all_formatters_handle_special_characters(self):
        """Test that formatters handle special characters."""
        transcript = [
            {"text": "Special: <>&\"'", "start": 0.0, "duration": 1.0},
        ]

        plain = format_plain(transcript)
        structured = format_structured(transcript)

        # All should contain the text (formatters don't escape)
        assert "Special: <>&\"'" in plain
        assert structured["entries"][0]["text"] == "Special: <>&\"'"

    def test_all_formatters_handle_newlines(self):
        """Test handling of text with newlines."""
        transcript = [
            {"text": "Line 1\nLine 2", "start": 0.0, "duration": 1.0},
        ]

        plain = format_plain(transcript)
        structured = format_structured(transcript)

        # All should preserve the newline in some form
        assert "Line 1" in plain
        assert "Line 2" in plain
        assert "Line 1\nLine 2" in structured["entries"][0]["text"]
