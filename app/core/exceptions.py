"""Custom exceptions for the application."""

from typing import Any


class APIError(Exception):
    """Base exception for API errors.

    Attributes:
        message: Error message describing what went wrong
        status_code: HTTP status code (default: 500)
        details: Optional additional error details
    """

    def __init__(self, message: str, status_code: int = 500, details: Any = None):
        """Initialize API error.

        Args:
            message: Error message describing what went wrong
            status_code: HTTP status code (default: 500)
            details: Optional additional error details
        """
        self.message = message
        self.status_code = status_code
        self.details = details
        super().__init__(self.message)


class AuthenticationError(APIError):
    """Raised when authentication fails."""

    def __init__(self, message: str = "Authentication failed", details: Any = None):
        """Initialize authentication error.

        Args:
            message: Error message (default: "Authentication failed")
            details: Optional additional error details
        """
        super().__init__(message, status_code=401, details=details)


class RateLimitExceeded(APIError):
    """Raised when rate limit is exceeded."""

    def __init__(self, message: str = "Rate limit exceeded", details: Any = None):
        """Initialize rate limit exceeded error.

        Args:
            message: Error message (default: "Rate limit exceeded")
            details: Optional additional error details
        """
        super().__init__(message, status_code=429, details=details)


class InvalidAPIKey(AuthenticationError):
    """Raised when API key is invalid."""

    def __init__(self, message: str = "Invalid API key"):
        """Initialize invalid API key error.

        Args:
            message: Error message (default: "Invalid API key")
        """
        super().__init__(message)


class DisabledAPIKey(AuthenticationError):
    """Raised when API key is disabled."""

    def __init__(self, message: str = "API key is disabled"):
        """Initialize disabled API key error.

        Args:
            message: Error message (default: "API key is disabled")
        """
        super().__init__(message)
