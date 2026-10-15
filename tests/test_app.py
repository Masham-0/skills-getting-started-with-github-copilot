import pytest
from fastapi.testclient import TestClient

import src.app as app_module


@pytest.fixture
def api_client(monkeypatch):
    activities = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu"],
        },
        "Art Club": {
            "description": "Explore drawing and painting",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 18,
            "participants": [],
        },
    }
    monkeypatch.setattr(app_module, "activities", activities)

    with TestClient(app_module.app) as client:
        yield client, activities


def test_get_activities_returns_all_activities(api_client):
    # Arrange
    client, activities = api_client

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert response.json() == activities


def test_signup_adds_participant(api_client):
    # Arrange
    client, activities = api_client
    email = "student@mergington.edu"

    # Act
    response = client.post("/activities/Art%20Club/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for Art Club"}
    assert email in activities["Art Club"]["participants"]


def test_signup_rejects_duplicate_participant(api_client):
    # Arrange
    client, activities = api_client
    email = "michael@mergington.edu"

    # Act
    response = client.post("/activities/Chess%20Club/signup", params={"email": email})

    # Assert
    assert response.status_code == 400
    assert response.json() == {"detail": "Student already signed up for this activity"}
    assert activities["Chess Club"]["participants"] == [email]


def test_signup_rejects_unknown_activity(api_client):
    # Arrange
    client, activities = api_client

    # Act
    response = client.post(
        "/activities/Unknown%20Club/signup",
        params={"email": "student@mergington.edu"},
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}
    assert activities["Art Club"]["participants"] == []


def test_unregister_removes_participant(api_client):
    # Arrange
    client, activities = api_client
    email = "michael@mergington.edu"

    # Act
    response = client.delete("/activities/Chess%20Club/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Removed {email} from Chess Club"}
    assert activities["Chess Club"]["participants"] == []


def test_unregister_rejects_nonparticipant(api_client):
    # Arrange
    client, activities = api_client
    email = "student@mergington.edu"

    # Act
    response = client.delete("/activities/Chess%20Club/signup", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Student is not signed up for this activity"}
    assert activities["Chess Club"]["participants"] == ["michael@mergington.edu"]


def test_unregister_rejects_unknown_activity(api_client):
    # Arrange
    client, activities = api_client

    # Act
    response = client.delete(
        "/activities/Unknown%20Club/signup",
        params={"email": "student@mergington.edu"},
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}
    assert activities["Art Club"]["participants"] == []