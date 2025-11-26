import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)

def test_get_activities():
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert isinstance(data["Chess Club"], dict)

def test_signup_and_unregister():
    test_email = "testuser@mergington.edu"
    activity = "Chess Club"

    # Ensure not already signed up
    client.delete(f"/activities/{activity}/unregister", params={"email": test_email})

    # Sign up
    response = client.post(f"/activities/{activity}/signup", params={"email": test_email})
    assert response.status_code == 200
    assert f"Signed up {test_email}" in response.json()["message"]

    # Check participant is added
    activities = client.get("/activities").json()
    assert test_email in activities[activity]["participants"]

    # Unregister
    response = client.delete(f"/activities/{activity}/unregister", params={"email": test_email})
    assert response.status_code == 200
    assert f"Unregistered {test_email}" in response.json()["message"]

    # Check participant is removed
    activities = client.get("/activities").json()
    assert test_email not in activities[activity]["participants"]

def test_signup_duplicate():
    test_email = "duplicate@mergington.edu"
    activity = "Programming Class"
    # Ensure not already signed up
    client.delete(f"/activities/{activity}/unregister", params={"email": test_email})
    # First signup
    client.post(f"/activities/{activity}/signup", params={"email": test_email})
    # Duplicate signup
    response = client.post(f"/activities/{activity}/signup", params={"email": test_email})
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"]
    # Cleanup
    client.delete(f"/activities/{activity}/unregister", params={"email": test_email})

def test_unregister_not_registered():
    test_email = "notregistered@mergington.edu"
    activity = "Gym Class"
    # Ensure not registered
    client.delete(f"/activities/{activity}/unregister", params={"email": test_email})
    # Try to unregister again
    response = client.delete(f"/activities/{activity}/unregister", params={"email": test_email})
    assert response.status_code == 400
    assert "not registered" in response.json()["detail"]
