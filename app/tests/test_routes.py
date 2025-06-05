from fastapi.testclient import TestClient

from app.main import app, get_db


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
    monkeypatch.setattr("app.main.intake_agent", lambda *_, **__: "ok")
    monkeypatch.setattr("app.main.fb_send_message", lambda *_, **__: None)
    monkeypatch.setattr("app.main.store_conversation", lambda *_, **__: 1)


def teardown_test():
    app.dependency_overrides.clear()


def test_message_route(monkeypatch):
    setup_test(monkeypatch)
    response = client.post(
        "/message",
        data={"From": "whatsapp:+123", "Body": "hi"},
    )
    assert response.status_code == 200
    teardown_test()
