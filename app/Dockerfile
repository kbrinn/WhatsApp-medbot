FROM python:3.11-slim
RUN pip install --no-cache-dir poetry

WORKDIR /app

COPY ../pyproject.toml ../poetry.lock ./

RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --no-root

COPY .. .

ENV PYTHONUNBUFFERED=1
#CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]


#FROM python:3.11-slim
#
## Install Poetry
#RUN pip install --no-cache-dir poetry
#
## Set workdir
#WORKDIR /app
#
## Copy metadata (README not needed when we skip packaging)
#COPY ./app/ .
#COPY ../pyproject.toml ../poetry.lock ./
#
#RUN poetry config virtualenvs.create false \
#    && poetry install --no-interaction --no-ansi --no-root
#
##EXPOSE 8000
#ENV PYTHONUNBUFFERED=1
