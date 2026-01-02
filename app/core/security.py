"""Security utilities for API key management."""

import bcrypt


def hash_api_key(api_key: str) -> str:
    """Hash an API key using bcrypt.

    Args:
        api_key: The plain API key to hash

    Returns:
        The bcrypt hash of the API key as a string
    """
    # bcrypt requires bytes input
    key_bytes = api_key.encode("utf-8")
    # Generate salt and hash
    hashed = bcrypt.hashpw(key_bytes, bcrypt.gensalt())
    # Return as string for database storage
    return hashed.decode("utf-8")


def verify_api_key(plain_key: str, hashed_key: str) -> bool:
    """Verify an API key against its hash.

    Args:
        plain_key: The plain API key to verify
        hashed_key: The bcrypt hash to verify against

    Returns:
        True if the key matches, False otherwise
    """
    try:
        # bcrypt requires bytes input
        key_bytes = plain_key.encode("utf-8")
        hash_bytes = hashed_key.encode("utf-8")
        return bcrypt.checkpw(key_bytes, hash_bytes)
    except Exception:
        return False
