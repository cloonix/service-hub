"""Pytest configuration and fixtures."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.cache import TTLCache
from app.core.rate_limit import RateLimiter
from app.database import Base, get_db
from app.main import app


@pytest.fixture
def db_session():
    """Create a test database session."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


@pytest.fixture
def test_cache():
    """Create a test cache instance."""
    return TTLCache(ttl_seconds=60, max_size=10, cache_dir=None)


@pytest.fixture
def test_rate_limiter():
    """Create a test rate limiter instance."""
    return RateLimiter(max_requests=5, window_seconds=60)


@pytest.fixture
def client(db_session, test_cache, test_rate_limiter):
    """Create a test client with dependency overrides."""

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    app.state.cache = test_cache
    app.state.rate_limiter = test_rate_limiter

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def test_api_key(db_session):
    """Create a test API key."""
    from app.services.api_key import APIKeyService

    api_key, full_key = APIKeyService.create_api_key(
        db=db_session, name="test-key", tier="free", rate_limit=100, rate_window=60
    )
    return {"model": api_key, "key": full_key}


@pytest.fixture
def admin_api_key(db_session):
    """Create an admin API key."""
    from app.services.api_key import APIKeyService

    api_key, full_key = APIKeyService.create_api_key(
        db=db_session, name="admin-key", tier="admin", rate_limit=10000, rate_window=60
    )
    return {"model": api_key, "key": full_key}
