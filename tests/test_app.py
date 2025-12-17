from fastapi.testclient import TestClient
import pytest

from src.app import app, activities

client = TestClient(app)


def test_get_activities_returns_200_and_structure():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    # check one known activity exists
    assert "Soccer" in data
    soccer = data["Soccer"]
    assert "description" in soccer
    assert "participants" in soccer


def test_signup_and_unregister_flow():
    activity = "Soccer"
    email = "test.user@example.com"

    # Ensure email not present initially
    if email in activities[activity]["participants"]:
        activities[activity]["participants"].remove(email)

    # Signup
    resp = client.post(f"/activities/{activity}/signup?email={email}")
    assert resp.status_code == 200
    assert resp.json()["message"].startswith("Signed up")
    assert email in activities[activity]["participants"]

    # Signing up same email again should fail
    resp2 = client.post(f"/activities/{activity}/signup?email={email}")
    assert resp2.status_code == 400

    # Unregister
    resp3 = client.delete(f"/activities/{activity}/participants?email={email}")
    assert resp3.status_code == 200
    assert resp3.json()["message"].startswith("Unregistered")
    assert email not in activities[activity]["participants"]


def test_signup_nonexistent_activity():
    resp = client.post("/activities/NoSuchActivity/signup?email=meh@example.com")
    assert resp.status_code == 404


def test_unregister_nonexistent_activity():
    resp = client.delete("/activities/NoSuchActivity/participants?email=meh@example.com")
    assert resp.status_code == 404


def test_unregister_not_signed_up():
    activity = "Basketball"
    email = "not.signed.up@example.com"

    # Ensure email not in participants
    if email in activities[activity]["participants"]:
        activities[activity]["participants"].remove(email)

    resp = client.delete(f"/activities/{activity}/participants?email={email}")
    assert resp.status_code == 400
