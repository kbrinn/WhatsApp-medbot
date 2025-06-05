import os

os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")  # noqa: E402

from fastapi.testclient import TestClient  # noqa: E402

from app.main import app, get_db  # noqa: E402


class DummyDB:
    def add(self, *_, **__):
        pass

    def commit(self):
        pass

    def rollback(self):
        pass


client = TestClient(app)


async def override_get_db():
    yield DummyDB()


def setup_test(monkeypatch):
    app.dependency_overrides[get_db] = override_get_db
    monkeypatch.setattr("app.main.intake_agent", lambda body: "ok")
    monkeypatch.setattr("app.main.fb_send_message", lambda *_, **__: None)
    monkeypatch.setattr("app.main.store_conversation", lambda *_, **__: 1)


def teardown_test():
    app.dependency_overrides.clear()


def test_verify_challenge(monkeypatch):
    monkeypatch.setenv("FB_VERIFY_TOKEN", "secret")
    setup_test(monkeypatch)

    response = client.get(
        "/facebook/webhook",
        params={
            "hub.mode": "subscribe",
            "hub.verify_token": "secret",
            "hub.challenge": "42",
        },
    )
    assert response.status_code == 200
    assert response.text == "42"

    teardown_test()


def test_facebook_webhook(monkeypatch):
    setup_test(monkeypatch)
    payload = {
        "entry": [
            {
                "changes": [
                    {"value": {"messages": [{"from": "123", "text": {"body": "hi"}}]}}
                ]
            }
        ]
    }
    response = client.post("/facebook/webhook", json=payload)
    assert response.status_code == 200

    teardown_test()
