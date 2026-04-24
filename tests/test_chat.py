from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_signup() -> None:
    res = client.post(
        "/api/auth/signup",
        json={"username": "testuser1", "password": "pass123"},
    )
    assert res.status_code in (200, 400)


def test_login_invalid() -> None:
    res = client.post(
        "/api/auth/login",
        json={"username": "nouser", "password": "wrong"},
    )
    assert res.status_code == 401


def test_signup_and_login() -> None:
    client.post(
        "/api/auth/signup",
        json={"username": "chatuser1", "password": "pass123"},
    )
    res = client.post(
        "/api/auth/login",
        json={"username": "chatuser1", "password": "pass123"},
    )
    assert res.status_code == 200
    assert "access_token" in res.json()


def test_get_users_without_token() -> None:
    res = client.get("/api/users/?token=invalidtoken")
    assert res.status_code == 401


def test_friend_request_flow() -> None:
    client.post("/api/auth/signup", json={"username": "user_a", "password": "pass"})
    client.post("/api/auth/signup", json={"username": "user_b", "password": "pass"})

    token_a = client.post(
        "/api/auth/login", json={"username": "user_a", "password": "pass"}
    ).json()["access_token"]

    token_b = client.post(
        "/api/auth/login", json={"username": "user_b", "password": "pass"}
    ).json()["access_token"]

    users = client.get(f"/api/users/?token={token_a}").json()
    user_b = next((u for u in users if u["username"] == "user_b"), None)
    assert user_b is not None

    req_res = client.post(f"/api/users/request/{user_b['id']}?token={token_a}")
    assert req_res.status_code == 200
    req_id = req_res.json()["id"]

    accept_res = client.post(
        f"/api/users/request/{req_id}/respond?action=accepted&token={token_b}"
    )
    assert accept_res.status_code == 200
    assert accept_res.json()["status"] == "accepted"

    friends = client.get(f"/api/users/friends?token={token_a}").json()
    assert any(f["username"] == "user_b" for f in friends)
