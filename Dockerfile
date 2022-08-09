FROM python:3.10.5-slim-buster

ARG depend
WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONBUFFERED 1

COPY pyproject.toml .
COPY . .
RUN pip install poetry==1.1.13 && \
    poetry config virtualenvs.create false && \
    poetry install ${depend} --no-interaction --no-ansi