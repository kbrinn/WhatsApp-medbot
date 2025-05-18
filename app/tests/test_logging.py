import logging

from fastapi.testclient import TestClient

from app.main import RequestValidator, app, get_db


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


def test_no_sensitive_logging(monkeypatch, caplog):
    monkeypatch.setenv("TWILIO_AUTH_TOKEN", "token")
    setup_test(monkeypatch)

    params = {"Body": "hi", "From": "whatsapp:+123", "MessageSid": "msg123"}
    validator = RequestValidator("token")
    signature = validator.compute_signature("http://testserver/message", params)

    with caplog.at_level(logging.INFO):
        client.post("/message", data=params, headers={"X-Twilio-Signature": signature})

    teardown_test()
    log_text = " ".join(record.getMessage() for record in caplog.records)
    assert "hi" not in log_text
    assert "+123" not in log_text
