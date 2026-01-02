"""YouTube transcript API routes."""

from typing import Any

from fastapi import APIRouter, Depends

from app.api.deps import check_rate_limit, get_cache
from app.core.cache import TTLCache
from app.models.api_key import APIKey
from lib.youtube import TranscriptService
from lib.youtube.models import LanguagesResponse, TranscriptRequest, TranscriptResponse

router = APIRouter(prefix="/youtube", tags=["YouTube"])


@router.post("/transcript", response_model=TranscriptResponse)
async def get_transcript(
    request: TranscriptRequest,
    api_key: APIKey = Depends(check_rate_limit),
    cache: TTLCache = Depends(get_cache),
) -> dict[str, Any]:
    """Fetch YouTube video transcript.

    Args:
        request: Transcript request with video ID and preferences
        api_key: Authenticated API key (rate limit checked)
        cache: Cache instance

    Returns:
        Transcript response with formatted transcript data
    """
    # Fetch transcript using core library
    service = TranscriptService(cache=cache)
    result = service.get_transcript(
        video_url_or_id=request.video_url_or_id,
        languages=request.languages,
        format_type=request.format_type,
    )

    return result.model_dump()


@router.get("/languages/{video_id}", response_model=LanguagesResponse)
async def list_languages(
    video_id: str,
    api_key: APIKey = Depends(check_rate_limit),
) -> dict[str, Any]:
    """List available transcript languages for a video.

    Args:
        video_id: YouTube video ID
        api_key: Authenticated API key (rate limit checked)

    Returns:
        List of available languages with metadata
    """
    # Fetch languages (no caching for language lists)
    service = TranscriptService(cache=None)
    result = service.list_languages(video_url_or_id=video_id)

    return result.model_dump()
