import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from api.main import app

@pytest.fixture
def client():
    """Fixture to provide a TestClient with mocked database."""
    # Mock the database session to avoid DATABASE_URL requirement
    with patch('api.main.get_db') as mock_get_db:
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        yield TestClient(app)
