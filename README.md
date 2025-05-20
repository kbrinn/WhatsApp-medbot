# WhatsApp MedBot

This project provides a FastAPI application that integrates with WhatsApp and various services.

## Environment Variables

Create a `.env` file based on the provided `.env.example` and fill in the values for your environment:

```
cp .env.example .env
```

Required variables:

- `DB_USER` – database user
- `DB_PASSWORD` – database user's password
- `DB_NAME` – name of the application database
- `DB_HOST` – database host (use `db` when running via Docker Compose)
- `DB_PORT` – database port
- `OPENAI_API_KEY` – key for OpenAI API access
- `TWILIO_ACCOUNT_SID` – Twilio account SID
- `TWILIO_AUTH_TOKEN` – Twilio auth token
- `TWILIO_PHONE_NUMBER` – Twilio phone number for messaging
- `FB_VERIFY_TOKEN` – token used to verify Facebook webhook
- `FB_ACCESS_TOKEN` – access token for the WhatsApp Business Cloud API
- `FB_PHONE_NUMBER_ID` – Facebook phone number ID for sending messages

## Running with Docker Compose

The `docker-compose.yml` file expects these environment variables to be available. Docker Compose automatically reads variables from a `.env` file in the project directory.

Run the application with:

```
docker-compose up --build
```
