"""YouTube transcript API routes."""

from fastapi import APIRouter, Depends

from app.api.deps import check_rate_limit, get_cache
from app.core.cache import TTLCache
from app.models.api_key import APIKey
from app.schemas.youtube import (
    LanguagesResponse,
    TranscriptRequest,
    TranscriptResponse,
)
from app.services.youtube import YouTubeService

router = APIRouter(prefix="/youtube", tags=["YouTube"])


@router.post("/transcript", response_model=TranscriptResponse)
async def get_transcript(
    request: TranscriptRequest,
    api_key: APIKey = Depends(check_rate_limit),
    cache: TTLCache = Depends(get_cache),
) -> dict:
    """Fetch YouTube video transcript.

    Args:
        request: Transcript request with video ID and preferences
        api_key: Authenticated API key (rate limit checked)
        cache: Cache instance

    Returns:
        Transcript response with formatted transcript data
    """
    # Fetch transcript
    service = YouTubeService(cache)
    result = service.get_transcript(
        request.video_url_or_id, request.languages, request.format_type
    )

    return result


@router.get("/languages/{video_id}", response_model=LanguagesResponse)
async def list_languages(
    video_id: str,
    api_key: APIKey = Depends(check_rate_limit),
) -> dict:
    """List available transcript languages for a video.

    Args:
        video_id: YouTube video ID
        api_key: Authenticated API key (rate limit checked)

    Returns:
        List of available languages with metadata
    """
    # Fetch languages (no caching for language lists)
    service = YouTubeService(cache=None)
    result = service.list_transcript_languages(video_id)

    return result
