# Third-party imports
import sys

from fastapi import Depends, FastAPI, Form, HTTPException, Request, Response
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.config import config

# Internal imports
from .agents.medical_intake_agent import intake_agent, user_patient_ids
from .services.facebook_service import send_message as fb_send_message
# Relative imports since main.py is in the same directory as services
from .services.models.models import SessionLocal
from .services.secure_storage import store_conversation
from .services.utils.utils import logger

app = FastAPI()


# Dependency
def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


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
                langchain_response = intake_agent(text, user_id=whatsapp_number)
                if whatsapp_number in user_patient_ids:
                    try:
                        conversation_id = store_conversation(
                            whatsapp_number,
                            text,
                            langchain_response,
                            db,
                            patient_id=user_patient_ids[whatsapp_number],
                        )
                        logger.info(
                            f"Conversation #{conversation_id} stored in database"
                        )
                    except SQLAlchemyError as e:
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
    langchain_response = intake_agent(Body, user_id=whatsapp_number)
    if whatsapp_number in user_patient_ids:
        try:
            conversation_id = store_conversation(
                whatsapp_number,
                Body,
                langchain_response,
                db,
                patient_id=user_patient_ids[whatsapp_number],
            )
            logger.info(f"Conversation #{conversation_id} stored in database")
        except SQLAlchemyError as e:  # pragma: no cover - DB issues are unlikely
            logger.error(f"Error storing conversation in database: {e}")
    fb_send_message(whatsapp_number, langchain_response)
    return ""


# New endpoint for local testing without Facebook API
@app.post("/local_test")
async def local_test(
    request: Request,
    message: str = Form(...),
    db: Session = Depends(get_db),
):
    """Test endpoint for local development without Facebook API."""
    test_number = "test_user_local"
    logger.info("Local test request received", message=message)

    langchain_response = intake_agent(message, user_id=test_number)
    if test_number in user_patient_ids:
        try:
            conversation_id = store_conversation(
                test_number,
                message,
                langchain_response,
                db,
                patient_id=user_patient_ids[test_number],
            )
            logger.info(
                f"Local test conversation #{conversation_id} stored in database"
            )
        except SQLAlchemyError as e:
            logger.error(f"Error storing local test conversation in database: {e}")

    return {"response": langchain_response}


# CLI function for running the chatbot in terminal
def run_cli_chat():
    """Run a command-line interface for the chatbot."""
    print("Welcome to the MedBot CLI. Type 'exit' to quit.")

    while True:
        user_input = input("\nYou: ")
        if user_input.lower() in ["exit", "quit"]:
            print("Goodbye!")
            break

        # Process the input through the medical intake agent
        response = intake_agent(user_input, user_id="cli_user")

        # Store conversation only after patient is registered
        if "cli_user" in user_patient_ids:
            try:
                store_conversation(
                    "cli_user",
                    user_input,
                    response,
                    patient_id=user_patient_ids["cli_user"],
                )
                print(f"\nMedBot: {response}")
            except Exception as e:
                print(f"\nMedBot: {response}")
                logger.error(f"Error storing CLI conversation: {e}")
        else:
            print(f"\nMedBot: {response}")


# Allow running the CLI directly
if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--cli":
        run_cli_chat()
    else:
        import uvicorn

        uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
