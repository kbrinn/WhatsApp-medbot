# WhatsApp MedBot

WhatsApp MedBot is a small FastAPI service that uses OpenAI via LangChain to collect patient intake information over WhatsApp. It stores conversations and basic patient details in a PostgreSQL database and can fill a PDF intake form when all required data has been gathered.

## Features

- **FastAPI** server with webhook endpoints for Facebook WhatsApp messages and a local testing route.
- **LangChain** powered `medical_intake_agent` that validates responses against the `PatientHistory` schema.
- **PostgreSQL** persistence for conversations and patient records (schema defined in `db/init/01_schema.sql`).
- **PDF generation** using `pdfrw` when an intake conversation completes.
- Optional **CLI** interface for manual testing (`python -m app.run_cli_chat`).

See `docs/security.md` for details on how PHI is kept out of the database.
See `docs/architecture.md` for a high-level overview of the project layout.
See `docs/improvements.md` for recommended next steps before production.

## Setup

1. Create a `.env` file in the repository root. The application and Docker compose read from this file. Required keys include:
   - `DB_USER`, `DB_PASSWORD`, `DB_NAME`, `DB_HOST`, `DB_PORT`
   - `OPENAI_API_KEY`
   - `FB_VERIFY_TOKEN`, `FB_ACCESS_TOKEN`, `FB_PHONE_NUMBER_ID`

2. Install dependencies with [Poetry](https://python-poetry.org/):

```bash
poetry install
```

## Running

The easiest way to start the stack is via Docker Compose:

```bash
docker-compose up --build
```

This launches the FastAPI app on port `8000` and a PostgreSQL database service. The app exposes several endpoints:

- `GET /facebook/webhook` – Facebook verification handshake
- `POST /facebook/webhook` – process WhatsApp messages
- `POST /message` – simple form endpoint for manual testing
- `POST /local_test` – local development endpoint that bypasses Facebook

You can also run the CLI chatbot locally:

```bash
python -m app.run_cli_chat
```

## Testing

Run the automated test suite with:

```bash
pytest
```

## License

This project is provided as-is for educational purposes.
