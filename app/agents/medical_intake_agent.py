import json
import os
from datetime import date
from pathlib import Path
from typing import Any, Dict, List

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from sqlalchemy.exc import SQLAlchemyError

from app.config import config
from app.services.models.models import SessionLocal
from app.services.secure_storage import store_patient
from app.services.utils.utils import logger

from .schemas.patient_form_EN import PatientHistory
from .tools_agent.pdf_filler_EN import fill_pdf

# Global dictionary to store conversation history by user ID
user_conversations: Dict[str, List[Any]] = {}

try:
    OPENAI_API_KEY = config("OPENAI_API_KEY")
except Exception as e:  # pragma: no cover - tested via fallback
    print(f"Error loading OPENAI_API_KEY from ..env file: {e}")
    OPENAI_API_KEY = ""


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


def intake_agent(query: str, user_id: str = "default_user") -> str:
    """
    Medical intake agent that collects patient information and validates it against the PatientHistory schema.

    Args:
        query: The patient's input message
        user_id: Unique identifier for the user (e.g., phone number)

    Returns:
        A response message from the agent, or validated patient data in JSON format when completed
    """
    if not OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY is not configured")

    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.0,
        openai_api_key=OPENAI_API_KEY,
    )

    # Bind the PDF generation tool for the final step
    llm.bind_tools([fill_pdf])

    # Get the directory of the current file (medical_intake_agent.py)
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # Navigate to the system_templates directory relative to the current file
    templates_path = os.path.join(current_dir, "system_templates", "patient_intake.txt")

    # Load the system prompt template
    system_text = Path(templates_path).read_text(encoding="utf-8")

    # Create a chat prompt template
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_text),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
        ]
    )

    # Initialize or get existing chat history for this user
    if user_id not in user_conversations:
        user_conversations[user_id] = []

    # Process the input
    chain = prompt | llm

    result = chain.invoke({"input": query, "chat_history": user_conversations[user_id]})

    # Update conversation history for this user
    user_conversations[user_id].append({"role": "human", "content": query})
    user_conversations[user_id].append({"role": "ai", "content": result.content})

    output = result.content

    # Check if this looks like the final JSON output (when patient says "done" or "END INTAKE")
    if "**END INTAKE**" in query or (
        output.strip().startswith("{") and output.strip().endswith("}")
    ):
        try:
            # Try to parse the output as JSON
            # First, extract JSON if there's any text before or after it
            if "{" in output and "}" in output:
                json_start = output.find("{")
                json_end = output.rfind("}") + 1
                json_str = output[json_start:json_end]
            else:
                json_str = output

            # Parse the JSON to a dictionary
            patient_data_dict = json.loads(json_str)

            # Handle date field conversions (dob and signature_date)
            if "dob" in patient_data_dict and patient_data_dict["dob"]:
                patient_data_dict["dob"] = date.fromisoformat(patient_data_dict["dob"])

            if (
                "signature_date" in patient_data_dict
                and patient_data_dict["signature_date"]
            ):
                patient_data_dict["signature_date"] = date.fromisoformat(
                    patient_data_dict["signature_date"]
                )

            # Validate against PatientHistory model
            patient_data = PatientHistory(**patient_data_dict)

            # Convert back to JSON string for output
            validated_json = patient_data.model_dump_json(indent=2)
            print("Successfully validated patient data against schema")

            # Insert patient's information into database table

            try:
                patient_row_id = store_patient(
                    #         patient_id=uuid.UUID(patient_data_dict["patient_id"]),
                    full_name=patient_data_dict["full_name"],
                    date_of_birth=patient_data_dict["dob"],
                    phone_e164=patient_data_dict["phone_e164"],
                    email=patient_data_dict.get("email"),
                    address_json=patient_data_dict.get("address"),
                )

                logger.info(f"Conversation #{patient_row_id} stored in database")
            except SQLAlchemyError as e:
                logger.error(f"Error storing conversation in database: {e}")

            # Clear the conversation history after successful completion
            user_conversations[user_id] = []

            # After successfully validating:
            pdf_path = fill_pdf(patient_data)
            return f"Patient intake form completed and validated:\n{validated_json}\n\nPDF form generated at: {pdf_path}"

        except Exception as e:
            # If validation fails, return error and original output
            print(f"Error validating patient data: {e}")
            return f"Patient provided this information, but validation failed: {e}\n\n{output}"

    # For normal conversation turns, just return the agent's response
    return output
