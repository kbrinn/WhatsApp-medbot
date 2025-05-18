
## Environment Variables

See `.env.example` for all required environment variables.

## Development

- Run tests: `poetry run pytest`
- Format code: `poetry run black .`
- Sort imports: `poetry run isort .`
- Lint code: `poetry run flake8`

## Architecture

This bot uses:
- FastAPI for the web framework
- LangChain for AI/LLM orchestration
- Twilio for WhatsApp integration
- PostgreSQL for data persistence
- AWS services for medical transcription

## License

MIT License