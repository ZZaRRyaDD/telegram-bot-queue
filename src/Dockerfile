FROM python:3.10.5-slim-buster

ARG MODE
ARG APP_HOME=/src

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONBUFFERED 1

COPY ./src ${APP_HOME}
WORKDIR ${APP_HOME}

RUN pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install ${MODE} --no-interaction --no-ansi
