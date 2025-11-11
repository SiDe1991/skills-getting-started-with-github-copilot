import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


class TestActivitiesAPI:
    """Test suite for the activities API endpoints."""

    def setup_method(self):
        """Reset activities data before each test."""
        # Save original activities
        self.original_activities = activities.copy()

    def teardown_method(self):
        """Restore original activities after each test."""
        activities.clear()
        activities.update(self.original_activities)

    @pytest.fixture
    def client(self):
        """Create a test client for the FastAPI app."""
        return TestClient(app)

    def test_root_redirect(self, client):
        """Test that root path redirects to static/index.html."""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"

    def test_get_activities(self, client):
        """Test GET /activities endpoint returns all activities."""
        response = client.get("/activities")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) > 0
        
        # Check that each activity has required fields
        for activity_name, activity_data in data.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)
            assert isinstance(activity_data["max_participants"], int)

    def test_signup_for_activity_success(self, client):
        """Test successful signup for an activity."""
        # Use an existing activity
        activity_name = "Chess Club"
        email = "newstudent@mergington.edu"
        
        # Ensure the student is not already signed up
        if email in activities[activity_name]["participants"]:
            activities[activity_name]["participants"].remove(email)
        
        response = client.post(f"/activities/{activity_name}/signup?email={email}")
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        assert activity_name in data["message"]
        
        # Verify the student was actually added
        assert email in activities[activity_name]["participants"]

    def test_signup_for_nonexistent_activity(self, client):
        """Test signup for an activity that doesn't exist."""
        activity_name = "Nonexistent Club"
        email = "student@mergington.edu"
        
        response = client.post(f"/activities/{activity_name}/signup?email={email}")
        assert response.status_code == 404
        
        data = response.json()
        assert data["detail"] == "Activity not found"

    def test_signup_duplicate_registration(self, client):
        """Test signup when student is already registered."""
        activity_name = "Chess Club"
        # Use an email that's already in the participants list
        email = "michael@mergington.edu"
        
        response = client.post(f"/activities/{activity_name}/signup?email={email}")
        assert response.status_code == 400
        
        data = response.json()
        assert data["detail"] == "Student is already signed up"

    def test_unregister_from_activity_success(self, client):
        """Test successful unregistration from an activity."""
        activity_name = "Chess Club"
        # Use an email that's already in the participants list
        email = "michael@mergington.edu"
        
        # Ensure the student is registered
        if email not in activities[activity_name]["participants"]:
            activities[activity_name]["participants"].append(email)
        
        response = client.delete(f"/activities/{activity_name}/unregister?email={email}")
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        assert activity_name in data["message"]
        
        # Verify the student was actually removed
        assert email not in activities[activity_name]["participants"]

    def test_unregister_from_nonexistent_activity(self, client):
        """Test unregister from an activity that doesn't exist."""
        activity_name = "Nonexistent Club"
        email = "student@mergington.edu"
        
        response = client.delete(f"/activities/{activity_name}/unregister?email={email}")
        assert response.status_code == 404
        
        data = response.json()
        assert data["detail"] == "Activity not found"

    def test_unregister_not_registered(self, client):
        """Test unregister when student is not registered."""
        activity_name = "Chess Club"
        email = "notregistered@mergington.edu"
        
        # Ensure the student is not registered
        if email in activities[activity_name]["participants"]:
            activities[activity_name]["participants"].remove(email)
        
        response = client.delete(f"/activities/{activity_name}/unregister?email={email}")
        assert response.status_code == 400
        
        data = response.json()
        assert data["detail"] == "Student is not registered for this activity"

    def test_activity_capacity_tracking(self, client):
        """Test that activity capacity is properly tracked."""
        response = client.get("/activities")
        assert response.status_code == 200
        
        data = response.json()
        
        # Verify capacity calculations
        for activity_name, activity_data in data.items():
            max_participants = activity_data["max_participants"]
            current_participants = len(activity_data["participants"])
            
            # Capacity should never be exceeded
            assert current_participants <= max_participants
            assert max_participants > 0

    def test_email_validation_in_urls(self, client):
        """Test that email parameters are properly handled in URLs."""
        activity_name = "Chess Club"
        
        # Test with email containing special characters
        email = "test.user+1@mergington.edu"
        
        # Ensure the student is not already signed up
        if email in activities[activity_name]["participants"]:
            activities[activity_name]["participants"].remove(email)
        
        # Test signup
        response = client.post(f"/activities/{activity_name}/signup?email={email}")
        assert response.status_code == 200
        
        # Test unregister
        response = client.delete(f"/activities/{activity_name}/unregister?email={email}")
        assert response.status_code == 200

    def test_activity_name_with_spaces(self, client):
        """Test activities with spaces in their names."""
        activity_name = "Programming Class"  # This has a space
        email = "testuser@mergington.edu"
        
        # Ensure the student is not already signed up
        if email in activities[activity_name]["participants"]:
            activities[activity_name]["participants"].remove(email)
        
        # Test signup with URL encoding
        response = client.post(f"/activities/{activity_name}/signup?email={email}")
        assert response.status_code == 200
        
        # Test unregister
        response = client.delete(f"/activities/{activity_name}/unregister?email={email}")
        assert response.status_code == 200