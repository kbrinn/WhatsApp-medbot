from __future__ import annotations

import os
from typing import List

from pydantic import UUID1
from sqlalchemy import Column, Integer, String, create_engine, DateTime, Date, JSON, UUID
from sqlalchemy.dialects.postgresql import BYTEA
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import declarative_base, sessionmaker

from pathlib import Path

from decouple import Config, RepositoryEnv, AutoConfig

# Base directory of the project (two levels up from this file)
BASE_DIR = Path(__file__).resolve().parent.parent

# ENV_FILE = BASE_DIR / ".env"
# if not ENV_FILE.exists():                     # fail fast if the file is missing
#     raise RuntimeError(f"Missing configuration file: {ENV_FILE}")
#
# config = Config(repository=RepositoryEnv(ENV_FILE))
config = AutoConfig(search_path=BASE_DIR)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _build_database_url() -> str:
    """
    Build the SQLAlchemy-compatible Postgres URL exclusively from the
    `.env` file. If `DATABASE_URL` is present we use it verbatim; otherwise
    the individual DB_* keys are combined. No values are read from
    os.environ – the .env file is the single source of truth.
    """
    # 1️⃣ Direct connection string in .env
    db_url = config("DATABASE_URL", default="")
    if db_url:
        if not db_url.startswith("postgresql"):
            raise RuntimeError(
                "DATABASE_URL must start with 'postgresql://'. "
                "Check the value in your `.env` file."
            )
        return db_url  # already complete

    # 2️⃣ Assemble from individual settings in .env
    required_keys: List[str] = ["DB_USER", "DB_PASSWORD", "DB_HOST", "DB_PORT", "DB_NAME"]
    missing = [key for key in required_keys if not config(key, default="")]
    if missing:
        raise RuntimeError(
            f"Missing database variables in .env: {', '.join(missing)}."
        )

    db_user = config("DB_USER")
    db_password = config("DB_PASSWORD")
    db_host = config("DB_HOST")
    db_port = config("DB_PORT")
    db_name = config("DB_NAME")

    return f"postgresql+psycopg2://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"


# ---------------------------------------------------------------------------
# SQLAlchemy setup
# ---------------------------------------------------------------------------

try:
    DATABASE_URL = _build_database_url()
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
    # Trigger an immediate connection to surface configuration errors early
    with engine.connect():  # noqa: WPS316
        pass
except OperationalError as exc:
    raise RuntimeError(
        "Could not connect to the PostgreSQL database. "
        "Confirm that the 'db' service is up and the credentials are correct."
    ) from exc

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()

# ---------------------------------------------------------------------------
# ORM models
# ---------------------------------------------------------------------------


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    sender = Column(String, nullable=False)
    message = Column(String, nullable=False)
    response = Column(String)

class Patient(Base):
    __tablename__ = "patient"
    patient_id = Column(UUID, primary_key=True, index=True)
    full_name = Column(BYTEA, nullable=False)
    date_of_birth = Column(Date, nullable=False)
    phone_e164 = Column(String, nullable=False)
    email = Column(String, nullable=True)
    address_json = Column(JSON, nullable=True)


