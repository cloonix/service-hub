"""YouTube transcript CLI tool.

Fetch YouTube video transcripts from the command line.
"""

import json
import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from lib.youtube import TranscriptService
from lib.youtube.models import FormatType

app = typer.Typer(
    name="youtube-transcript",
    help="""YouTube transcript CLI tool - fetch video transcripts in multiple formats.

Examples:

  # Get English transcript (default)
  youtube-transcript get-transcript dQw4w9WgXcQ

  # Get Spanish transcript
  youtube-transcript get-transcript dQw4w9WgXcQ -l es

  # Try multiple languages (fallback)
  youtube-transcript get-transcript dQw4w9WgXcQ -l en -l es

  # List available languages first
  youtube-transcript list-languages dQw4w9WgXcQ

  # Save as JSON with timestamps
  youtube-transcript get-transcript dQw4w9WgXcQ -f json -o output.json

Commands:
  get-transcript   Fetch video transcript
  list-languages   Show available languages for a video
  version          Show version information
""",
    add_completion=False,
)
console = Console()


@app.command()
def get_transcript(
    video: str = typer.Argument(..., help="YouTube video URL or ID"),
    lang: list[str] = typer.Option(
        ["en"],
        "--lang",
        "-l",
        help="Language code (e.g., 'en', 'es', 'fr'). Can be specified multiple times for fallback languages. Use 'list-languages' command to see available languages.",
    ),
    format: str = typer.Option(
        "plain",
        "--format",
        "-f",
        help="Output format: plain, json",
    ),
    output: Optional[str] = typer.Option(
        None, "--output", "-o", help="Save to file instead of stdout"
    ),
) -> None:
    """Fetch YouTube video transcript.

    Examples:

        # Get English transcript (default)
        youtube-transcript get-transcript dQw4w9WgXcQ

        # Get Spanish transcript
        youtube-transcript get-transcript dQw4w9WgXcQ -l es

        # Try English first, fallback to Spanish if not available
        youtube-transcript get-transcript dQw4w9WgXcQ -l en -l es

        # Get JSON format with timestamps and save to file
        youtube-transcript get-transcript dQw4w9WgXcQ -f json -o transcript.json

        # List available languages for a video first
        youtube-transcript list-languages dQw4w9WgXcQ
    """
    # Validate format
    valid_formats = ["plain", "json"]
    if format not in valid_formats:
        console.print(
            f"[red]✗[/red] Invalid format: {format}. Must be one of: {', '.join(valid_formats)}",
            style="red",
        )
        raise typer.Exit(1)

    # Map 'json' to 'structured' for the service
    service_format = "structured" if format == "json" else format

    # Create service and fetch transcript
    service = TranscriptService()

    with console.status(f"[bold blue]Fetching transcript for {video}..."):
        result = service.get_transcript(
            video_url_or_id=video,
            languages=lang,
            format_type=service_format,
        )

    # Handle errors
    if not result.success:
        console.print(f"[red]✗[/red] Error: {result.message}", style="red")
        # Use specific exit codes for different errors
        error_codes = {
            "INVALID_VIDEO_ID": 2,
            "NO_TRANSCRIPT_FOUND": 3,
            "VIDEO_UNAVAILABLE": 4,
            "TRANSCRIPTS_DISABLED": 5,
        }
        exit_code = error_codes.get(result.error or "UNKNOWN_ERROR", 1)
        raise typer.Exit(exit_code)

    # Prepare output
    if format == "json":
        # Convert to JSON string
        output_text = json.dumps(result.transcript, indent=2)
    else:
        # For plain format, transcript is a string
        output_text = str(result.transcript or "")

    # Write to file or stdout
    if output:
        output_path = Path(output)
        output_path.write_text(str(output_text))
        console.print(
            f"[green]✓[/green] Transcript saved to [bold]{output}[/bold]",
            style="green",
        )
        console.print(
            f"  Video ID: {result.video_id} | Language: {result.language} | "
            f"Auto-generated: {result.is_generated}"
        )
    else:
        # Output to stdout (no colors for piping)
        print(output_text)

    # Success
    raise typer.Exit(0)


@app.command()
def list_languages(
    video: str = typer.Argument(..., help="YouTube video URL or ID"),
    json_output: bool = typer.Option(
        False, "--json", help="Output as JSON instead of table"
    ),
) -> None:
    """List available transcript languages for a video.

    Examples:

        # Show available languages as a table
        youtube-transcript list-languages dQw4w9WgXcQ

        # Get languages as JSON
        youtube-transcript list-languages dQw4w9WgXcQ --json
    """
    # Create service and fetch languages
    service = TranscriptService()

    with console.status(f"[bold blue]Fetching available languages for {video}..."):
        result = service.list_languages(video_url_or_id=video)

    # Handle errors
    if not result.success:
        console.print(f"[red]✗[/red] Error: {result.message}", style="red")
        error_codes = {
            "INVALID_VIDEO_ID": 2,
            "NO_TRANSCRIPT_FOUND": 3,
            "VIDEO_UNAVAILABLE": 4,
            "TRANSCRIPTS_DISABLED": 5,
        }
        exit_code = error_codes.get(result.error or "UNKNOWN_ERROR", 1)
        raise typer.Exit(exit_code)

    # Output as JSON
    if json_output:
        output = {
            "video_id": result.video_id,
            "languages": [lang.model_dump() for lang in (result.languages or [])],
        }
        print(json.dumps(output, indent=2))
        raise typer.Exit(0)

    # Output as table
    if not result.languages:
        console.print(
            f"[yellow]No languages found for video {result.video_id}[/yellow]"
        )
        raise typer.Exit(0)

    table = Table(title=f"Available Languages for {result.video_id}")
    table.add_column("Code", style="cyan", no_wrap=True)
    table.add_column("Name", style="white")
    table.add_column("Auto-generated", style="yellow")
    table.add_column("Translatable", style="green")

    for lang in result.languages:
        table.add_row(
            lang.code,
            lang.name,
            "Yes" if lang.is_generated else "No",
            "Yes" if lang.is_translatable else "No",
        )

    console.print(table)
    console.print(f"\n[dim]Found {len(result.languages)} available language(s)[/dim]")
    raise typer.Exit(0)


@app.command()
def version() -> None:
    """Show version information."""
    console.print("[bold]YouTube Transcript CLI[/bold]")
    console.print("Version: 1.0.0")
    console.print("Part of Service Hub")
    raise typer.Exit(0)


def main() -> None:
    """Entry point for the CLI."""
    app()


if __name__ == "__main__":
    main()
