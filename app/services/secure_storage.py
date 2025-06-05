"""Utility for storing conversations in the database."""

import uuid
from datetime import date
from typing import Any

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from .models.models import Conversation, Patient, SessionLocal


def store_conversation(
    sender: str,
    message: str,
    response: str,
    db: Session | None = None,
    *,
    patient_id: uuid.UUID | None = None,
) -> int:
    """Persist a conversation to the database and return the row ID."""

    created_session = False
    if db is None:
        db = SessionLocal()
        created_session = True

    try:
        conversation = Conversation(
            sender=sender,
            message=message,
            response=response,
            patient_id=patient_id,
        )
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
        return conversation.id
    except SQLAlchemyError:
        db.rollback()
        raise
    finally:
        if created_session:
            db.close()


def store_patient(
    *,
    full_name: bytes,
    date_of_birth: date,
    phone_e164: str,
    email: str | None,
    address_json: dict[str, Any] | str,
    db: Session | None = None,
) -> uuid.UUID:

    created_session = False
    if db is None:
        db = SessionLocal()
        created_session = True

    try:
        patient = Patient(
            full_name=full_name,
            date_of_birth=date_of_birth,
            phone_e164=phone_e164,
            email=email,
            address_json=address_json,
        )
        db.add(patient)
        db.commit()
        db.refresh(patient)

        return patient.patient_id

    except SQLAlchemyError:
        db.rollback()
        raise
    finally:
        if created_session:
            db.close()
