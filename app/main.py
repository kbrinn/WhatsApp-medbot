# Third-party imports
import openai
from decouple import config
from fastapi import Depends, FastAPI, Form, HTTPException, Request

# Relative imports since main.py is in the same directory as services
from services.models.models import Conversation, SessionLocal
from services.utils.utils import logger, send_message
from services.secure_storage import store_conversation
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

# Internal imports


try:
    from twilio.request_validator import RequestValidator  # type: ignore
except Exception:  # pragma: no cover - fallback when twilio isn't installed
    import base64
    import hashlib
    import hmac

    class RequestValidator:  # type: ignore
        """Simple fallback implementation of Twilio's RequestValidator."""

        def __init__(self, token: str):
            self.token = token

        def compute_signature(self, url: str, params: dict) -> str:
            data = url
            for key in sorted(params):
                data += key + params[key]
            digest = hmac.new(self.token.encode(), data.encode(), hashlib.sha1).digest()
            return base64.b64encode(digest).decode()

        def validate(self, url: str, params: dict, signature: str) -> bool:
            expected = self.compute_signature(url, params)
            return hmac.compare_digest(expected, signature)


from agents.medical_intake_agent import intake_agent

app = FastAPI()


# Dependency
def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


@app.post("/message")
async def reply(request: Request, Body: str = Form(), db: Session = Depends(get_db)):
    try:
        # Extract the phone number from the incoming webhook request
        form_data = await request.form()
        message_id = form_data.get("MessageSid", "unknown")
        logger.info("received_message", message_id=message_id)

        # Validate Twilio signature
        signature = request.headers.get("X-Twilio-Signature", "")
        validator = RequestValidator(config("TWILIO_AUTH_TOKEN"))
        if not validator.validate(str(request.url), dict(form_data), signature):
            logger.warning("Invalid Twilio signature")
            raise HTTPException(status_code=403, detail="Invalid signature")

        whatsapp_number = form_data["From"].split("whatsapp:")[-1]
        masked_number = f"{whatsapp_number[:2]}***"
        logger.info("send_response", to=masked_number)

        # Get the generated text from the LangChain agent
        langchain_response = intake_agent(Body)

        # Store PHI in protected storage and only save a reference ID
        reference_id = store_conversation(
            whatsapp_number,
            Body,
            langchain_response,
        )
        try:
            conversation = Conversation(
                sender=whatsapp_number,
                message=reference_id,
                response=reference_id,
            )
            db.add(conversation)
            db.commit()
            logger.info(f"Conversation #{conversation.id} stored in database")
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Error storing conversation in database: {e}")

        send_message(whatsapp_number, langchain_response)
        return ""
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
        return {"error": str(e)}
