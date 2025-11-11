import pytest
from fastapi.testclient import TestClient
from src.app import app

@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)

@pytest.fixture
def sample_activities():
    """Sample activities data for testing."""
    return {
        "Test Club": {
            "description": "A test club for testing purposes",
            "schedule": "Mondays, 3:00 PM - 4:00 PM",
            "max_participants": 5,
            "participants": ["test1@mergington.edu", "test2@mergington.edu"]
        },
        "Empty Club": {
            "description": "A club with no participants",
            "schedule": "Tuesdays, 4:00 PM - 5:00 PM",
            "max_participants": 10,
            "participants": []
        }
    }