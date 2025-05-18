from fastapi.testclient import TestClient
from app.main import app, get_db, RequestValidator


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
    monkeypatch.setattr("app.main.send_message", lambda *_, **__: None)


def teardown_test():
    app.dependency_overrides.clear()


def test_reply_valid_signature(monkeypatch):
    monkeypatch.setenv("TWILIO_AUTH_TOKEN", "token")
    setup_test(monkeypatch)

    params = {"Body": "hi", "From": "whatsapp:+123"}
    validator = RequestValidator("token")
    signature = validator.compute_signature("http://testserver/message", params)

    response = client.post("/message", data=params, headers={"X-Twilio-Signature": signature})
    assert response.status_code == 200

    teardown_test()


def test_reply_invalid_signature(monkeypatch):
    monkeypatch.setenv("TWILIO_AUTH_TOKEN", "token")
    setup_test(monkeypatch)

    params = {"Body": "hi", "From": "whatsapp:+123"}

    response = client.post("/message", data=params, headers={"X-Twilio-Signature": "bad"})
    assert response.status_code == 403

    teardown_test()

