"""Middleware for FastAPI application."""

from app.middleware.request_size import RequestSizeLimitMiddleware

__all__ = ["RequestSizeLimitMiddleware"]
