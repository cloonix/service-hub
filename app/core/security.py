"""Security utilities for API key management."""

from passlib.context import CryptContext

# Password hashing context using bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_api_key(api_key: str) -> str:
    """Hash an API key using bcrypt.

    Args:
        api_key: The plain API key to hash

    Returns:
        The bcrypt hash of the API key
    """
    return pwd_context.hash(api_key)


def verify_api_key(plain_key: str, hashed_key: str) -> bool:
    """Verify an API key against its hash.

    Args:
        plain_key: The plain API key to verify
        hashed_key: The bcrypt hash to verify against

    Returns:
        True if the key matches, False otherwise
    """
    return pwd_context.verify(plain_key, hashed_key)
