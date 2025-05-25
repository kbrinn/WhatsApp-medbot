"""Utility for storing conversations in the database."""

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from .models.models import Conversation, SessionLocal


def store_conversation(
    sender: str,
    message: str,
    response: str,
    db: Session | None = None,
) -> int:
    """Persist a conversation to the database and return the row ID."""

    created_session = False
    if db is None:
        db = SessionLocal()
        created_session = True

    try:
        conversation = Conversation(sender=sender, message=message, response=response)
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
