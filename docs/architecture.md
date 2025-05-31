# Project Architecture

This document provides an internal overview of how **WhatsApp MedBot** is organized and how the main pieces fit together.

## Scope
- Collect patient intake information over WhatsApp and validate it against the structured `PatientHistory` schema.
- Store conversations and patient records in PostgreSQL.
- Generate a filled PDF intake form once the required data is captured.

## Directory Layout
- `app/` – source code for the FastAPI service
  - `main.py` exposes webhook endpoints (`/facebook/webhook`, `/message`, and `/local_test`) and invokes the `intake_agent` from the agents package.
  - `agents/` – LangChain powered intake agent (`medical_intake_agent.py`) with schema definitions and PDF tools.
  - `services/` – infrastructure helpers including the Facebook API wrapper, database models and the secure storage logic.
  - `routes/` – legacy Twilio webhook stubs.
  - `tests/` – minimal unit tests for the API routes.
- `db/` – PostgreSQL docker image and `init/01_schema.sql` which creates the tables.
- `docs/` – documentation such as `security.md` and this overview.

## Data Flow
1. A WhatsApp message triggers the `/facebook/webhook` endpoint.
2. `main.py` passes the message to `intake_agent` which uses OpenAI via LangChain to ask follow up questions.
3. Each turn is stored using `store_conversation` in `app/services/secure_storage.py` and a reply is sent back through `facebook_service.send_message`.
4. When the patient provides all required information the agent validates the data using the `PatientHistory` model and `fill_pdf` generates a PDF in `app/services/database/data/`.

## Database Schema
`db/init/01_schema.sql` creates tables for `conversations`, `patient`, and additional scheduling related tables. Conversations store only reference IDs to keep PHI out of the database. See `docs/security.md` for details.

## Development Notes
- Configure environment variables in `.env` before running Docker Compose.
- The service can also be used from the command line via `python -m app.run_cli_chat` for local testing.

