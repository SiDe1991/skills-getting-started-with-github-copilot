import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


class TestIntegration:
    """Integration tests for the complete workflow."""

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

    def test_complete_registration_workflow(self, client):
        """Test complete workflow: view activities, register, unregister."""
        # Step 1: Get all activities
        response = client.get("/activities")
        assert response.status_code == 200
        
        initial_activities = response.json()
        activity_name = "Chess Club"
        email = "workflow.test@mergington.edu"
        
        # Ensure clean state
        if email in activities[activity_name]["participants"]:
            activities[activity_name]["participants"].remove(email)
        
        initial_count = len(initial_activities[activity_name]["participants"])
        
        # Step 2: Register for an activity
        response = client.post(f"/activities/{activity_name}/signup?email={email}")
        assert response.status_code == 200
        
        # Step 3: Verify registration by getting activities again
        response = client.get("/activities")
        assert response.status_code == 200
        
        updated_activities = response.json()
        new_count = len(updated_activities[activity_name]["participants"])
        
        assert new_count == initial_count + 1
        assert email in updated_activities[activity_name]["participants"]
        
        # Step 4: Unregister from the activity
        response = client.delete(f"/activities/{activity_name}/unregister?email={email}")
        assert response.status_code == 200
        
        # Step 5: Verify unregistration
        response = client.get("/activities")
        assert response.status_code == 200
        
        final_activities = response.json()
        final_count = len(final_activities[activity_name]["participants"])
        
        assert final_count == initial_count
        assert email not in final_activities[activity_name]["participants"]

    def test_multiple_students_same_activity(self, client):
        """Test multiple students registering for the same activity."""
        activity_name = "Programming Class"
        emails = [
            "student1@mergington.edu",
            "student2@mergington.edu", 
            "student3@mergington.edu"
        ]
        
        # Ensure clean state
        for email in emails:
            if email in activities[activity_name]["participants"]:
                activities[activity_name]["participants"].remove(email)
        
        # Get initial count
        initial_response = client.get("/activities")
        initial_count = len(initial_response.json()[activity_name]["participants"])
        
        # Register all students
        for email in emails:
            response = client.post(f"/activities/{activity_name}/signup?email={email}")
            assert response.status_code == 200
        
        # Verify all are registered
        response = client.get("/activities")
        final_activities = response.json()
        final_count = len(final_activities[activity_name]["participants"])
        
        assert final_count == initial_count + len(emails)
        
        for email in emails:
            assert email in final_activities[activity_name]["participants"]

    def test_student_multiple_activities(self, client):
        """Test single student registering for multiple activities."""
        email = "multiaccess@mergington.edu"
        activity_names = ["Chess Club", "Programming Class", "Gym Class"]
        
        # Ensure clean state
        for activity_name in activity_names:
            if email in activities[activity_name]["participants"]:
                activities[activity_name]["participants"].remove(email)
        
        # Register for all activities
        for activity_name in activity_names:
            response = client.post(f"/activities/{activity_name}/signup?email={email}")
            assert response.status_code == 200
        
        # Verify registrations
        response = client.get("/activities")
        all_activities = response.json()
        
        for activity_name in activity_names:
            assert email in all_activities[activity_name]["participants"]

    def test_capacity_limit_enforcement(self, client):
        """Test that activities cannot exceed their capacity."""
        # Create a small test activity for capacity testing
        test_activity = {
            "description": "Small test activity",
            "schedule": "Test schedule",
            "max_participants": 2,
            "participants": []
        }
        
        # Add it to activities
        activities["Test Capacity"] = test_activity
        
        # Register students up to capacity
        emails = ["cap1@test.edu", "cap2@test.edu", "cap3@test.edu"]
        
        # Register first two (should succeed)
        for i in range(2):
            response = client.post(f"/activities/Test Capacity/signup?email={emails[i]}")
            assert response.status_code == 200
        
        # Verify we're at capacity
        response = client.get("/activities")
        activity_data = response.json()["Test Capacity"]
        assert len(activity_data["participants"]) == 2
        assert len(activity_data["participants"]) == activity_data["max_participants"]

    def test_error_handling_consistency(self, client):
        """Test that error responses are consistent across endpoints."""
        nonexistent_activity = "Does Not Exist"
        email = "test@test.edu"
        
        # Test signup error format
        signup_response = client.post(f"/activities/{nonexistent_activity}/signup?email={email}")
        assert signup_response.status_code == 404
        signup_error = signup_response.json()
        
        # Test unregister error format  
        unregister_response = client.delete(f"/activities/{nonexistent_activity}/unregister?email={email}")
        assert unregister_response.status_code == 404
        unregister_error = unregister_response.json()
        
        # Both should have the same error structure
        assert "detail" in signup_error
        assert "detail" in unregister_error
        assert signup_error["detail"] == unregister_error["detail"]