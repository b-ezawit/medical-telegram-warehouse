import os
import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient

# Set dummy DATABASE_URL before importing app
os.environ['DATABASE_URL'] = 'postgresql://user:password@localhost/test_db'

@pytest.fixture
def client():
    """Fixture to provide a TestClient with mocked database for testing."""
    from api.main import app
    with patch('api.database.SessionLocal') as mock_session_local:
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db
        yield TestClient(app)
