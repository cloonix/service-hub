"""Request size limit middleware to protect against large payloads."""

from typing import Any

from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware


class RequestSizeLimitMiddleware(BaseHTTPMiddleware):
    """Middleware to enforce maximum request body size limits.

    This middleware protects the API from large payload attacks and
    accidental memory exhaustion by rejecting requests that exceed
    the configured maximum size.

    Attributes:
        max_size: Maximum allowed request body size in bytes
    """

    def __init__(self, app: Any, max_size: int = 1_000_000) -> None:
        """Initialize request size limit middleware.

        Args:
            app: FastAPI application instance
            max_size: Maximum request body size in bytes (default: 1MB)
        """
        super().__init__(app)
        self.max_size = max_size

    async def dispatch(self, request: Request, call_next: Any) -> JSONResponse | Any:
        """Check request size before processing.

        Args:
            request: Incoming HTTP request
            call_next: Next middleware or endpoint to call

        Returns:
            HTTP response (413 if too large, otherwise response from next handler)
        """
        # Check Content-Length header if present
        content_length = request.headers.get("content-length")

        if content_length:
            try:
                content_length_int = int(content_length)
                if content_length_int > self.max_size:
                    return JSONResponse(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        content={
                            "success": False,
                            "error": "PayloadTooLarge",
                            "message": f"Request body too large. Maximum size: {self.max_size:,} bytes ({self.max_size // 1024:,} KB)",
                        },
                    )
            except ValueError:
                # Invalid Content-Length header - let it through and fail naturally
                pass

        return await call_next(request)
