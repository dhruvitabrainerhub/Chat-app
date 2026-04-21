from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def setup_function() -> None:
    client.delete("/api/messages?room=general")


def test_get_rooms() -> None:
    res = client.get("/api/rooms")
    assert res.status_code == 200
    assert len(res.json()) > 0


def test_send_message() -> None:
    res = client.post(
        "/api/messages",
        json={"username": "Alice", "room": "general", "text": "Hello!"},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["username"] == "Alice"
    assert data["text"] == "Hello!"


def test_get_messages() -> None:
    client.post(
        "/api/messages",
        json={"username": "Bob", "room": "general", "text": "Hi Bob!"},
    )
    res = client.get("/api/messages?room=general")
    assert res.status_code == 200
    assert len(res.json()) >= 1


def test_empty_message_rejected() -> None:
    res = client.post(
        "/api/messages",
        json={"username": "Alice", "room": "general", "text": "   "},
    )
    assert res.status_code == 400
