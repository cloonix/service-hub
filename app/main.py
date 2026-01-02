"""Main FastAPI application."""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse

from app.api.v1 import admin, health, youtube
from app.config import settings
from app.core.cache import TTLCache
from app.core.exceptions import APIError
from app.core.rate_limit import RateLimiter
from app.database import init_db

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager for startup and shutdown events.

    Args:
        app: FastAPI application instance

    Yields:
        None during application lifetime
    """
    # Startup
    logger.info("Starting up application...")

    # Initialize database
    init_db()

    # Ensure directories exist
    settings.ensure_directories()

    # Initialize cache
    app.state.cache = TTLCache(
        ttl_seconds=settings.CACHE_TTL,
        max_size=settings.CACHE_MAX_SIZE,
        cache_dir=settings.CACHE_DIR if settings.CACHE_ENABLED else None,
    )

    # Initialize rate limiter with tier-based limits
    tier_limits = {
        "free": (100, 60),  # 100 requests per minute
        "premium": (1000, 60),  # 1000 requests per minute
        "admin": (10000, 60),  # 10000 requests per minute
    }
    app.state.rate_limiter = RateLimiter(
        max_requests=settings.DEFAULT_RATE_LIMIT,
        window_seconds=settings.DEFAULT_RATE_WINDOW,
        limits_per_tier=tier_limits,
    )

    logger.info("Application started successfully")

    yield

    # Shutdown
    logger.info("Shutting down application...")
    app.state.cache.clear()
    logger.info("Application shutdown complete")


# Create FastAPI app
app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    description=settings.API_DESCRIPTION,
    debug=settings.DEBUG,
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add compression middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)


# Exception handlers
@app.exception_handler(APIError)
async def api_error_handler(request: Request, exc: APIError) -> JSONResponse:
    """Handle custom API errors.

    Args:
        request: FastAPI request
        exc: API error exception

    Returns:
        JSON error response
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": exc.__class__.__name__,
            "message": exc.message,
            "details": exc.details,
        },
    )


@app.exception_handler(RequestValidationError)
async def validation_error_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Handle request validation errors.

    Args:
        request: FastAPI request
        exc: Validation error

    Returns:
        JSON error response
    """
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "error": "ValidationError",
            "message": "Invalid request data",
            "details": exc.errors(),
        },
    )


# Include routers
app.include_router(health.router)
app.include_router(youtube.router, prefix="/api/v1")
app.include_router(admin.router, prefix="/api/v1")


@app.get("/")
async def root() -> dict:
    """Root endpoint.

    Returns:
        Welcome message with API information
    """
    return {
        "message": "YouTube Transcript API",
        "version": settings.API_VERSION,
        "docs": "/docs",
        "health": "/health",
    }
