# Third-party imports
# Internal imports
from agents.medical_intake_agent import intake_agent
from decouple import config
from fastapi import Depends, FastAPI, Form, HTTPException, Request, Response
from services.facebook_service import send_message as fb_send_message

# Relative imports since main.py is in the same directory as services
from services.models.models import Conversation, SessionLocal
from services.secure_storage import store_conversation
from services.utils.utils import logger
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

app = FastAPI()


@app.get("/facebook/webhook")
async def facebook_verify(request: Request) -> Response:
    """Verify the Facebook webhook challenge."""
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")
    if mode == "subscribe" and token == config("FB_VERIFY_TOKEN"):
        return Response(content=challenge or "")
    raise HTTPException(status_code=403, detail="Verification failed")


@app.post("/facebook/webhook")
async def facebook_webhook(request: Request, db: Session = Depends(get_db)):
    """Handle incoming Facebook WhatsApp messages."""
    data = await request.json()
    for entry in data.get("entry", []):
        for change in entry.get("changes", []):
            value = change.get("value", {})
            for message in value.get("messages", []):
                whatsapp_number = message.get("from")
                text = message.get("text", {}).get("body", "")
                if not whatsapp_number or not text:
                    continue
                langchain_response = intake_agent(text)
                reference_id = store_conversation(
                    whatsapp_number,
                    text,
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
                fb_send_message(whatsapp_number, langchain_response)
    return ""


# Simple message endpoint for manual testing
@app.post("/message")
async def reply(
    request: Request,
    From: str = Form(...),
    Body: str = Form(...),
    db: Session = Depends(get_db),
):
    """Handle generic form-based messages and reply via Facebook's API."""
    whatsapp_number = From.split("whatsapp:")[-1]
    masked_number = f"{whatsapp_number[:2]}***"
    logger.info("send_response", to=masked_number)
    langchain_response = intake_agent(Body)
    reference_id = store_conversation(whatsapp_number, Body, langchain_response)
    try:
        conversation = Conversation(
            sender=whatsapp_number,
            message=reference_id,
            response=reference_id,
        )
        db.add(conversation)
        db.commit()
        logger.info(f"Conversation #{conversation.id} stored in database")
    except SQLAlchemyError as e:  # pragma: no cover - DB issues are unlikely
        db.rollback()
        logger.error(f"Error storing conversation in database: {e}")
    fb_send_message(whatsapp_number, langchain_response)
    return ""


# Dependency
def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()
