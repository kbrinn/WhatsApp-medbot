# Third-party imports
import openai
from fastapi import FastAPI, Form, Depends, Request
from decouple import config
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

# Internal imports

# Relative imports since main.py is in the same directory as services
from services.models.models import Conversation, SessionLocal
from services.utils.utils import send_message, logger
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
        logger.info(f"Received form data: {dict(form_data)}")
        
        whatsapp_number = form_data['From'].split("whatsapp:")[-1]
        print(f"Sending the LangChain response to this number: {whatsapp_number}")

        # Get the generated text from the LangChain agent
        langchain_response = intake_agent(Body)

        # Store the conversation in the database
        try:
            conversation = Conversation(
                sender=whatsapp_number,
                message=Body,
                response=langchain_response
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