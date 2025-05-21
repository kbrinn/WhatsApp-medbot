FROM python:3.11-slim

# Install Poetry
RUN pip install --no-cache-dir poetry

# Set workdir
WORKDIR /app

# Copy project files
COPY pyproject.toml poetry.lock ./
RUN poetry config virtualenvs.create false \
    && poetry install --no-dev --no-interaction --no-ansi

COPY . .

EXPOSE 8000
ENV PYTHONUNBUFFERED=1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
