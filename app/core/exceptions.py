"""Custom exceptions for the application."""

from typing import Any


class APIError(Exception):
    """Base exception for API errors."""

    def __init__(self, message: str, status_code: int = 500, details: Any = None):
        self.message = message
        self.status_code = status_code
        self.details = details
        super().__init__(self.message)


class AuthenticationError(APIError):
    """Raised when authentication fails."""

    def __init__(self, message: str = "Authentication failed", details: Any = None):
        super().__init__(message, status_code=401, details=details)


class RateLimitExceeded(APIError):
    """Raised when rate limit is exceeded."""

    def __init__(self, message: str = "Rate limit exceeded", details: Any = None):
        super().__init__(message, status_code=429, details=details)


class InvalidAPIKey(AuthenticationError):
    """Raised when API key is invalid."""

    def __init__(self, message: str = "Invalid API key"):
        super().__init__(message)


class DisabledAPIKey(AuthenticationError):
    """Raised when API key is disabled."""

    def __init__(self, message: str = "API key is disabled"):
        super().__init__(message)
