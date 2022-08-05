FROM python:3.10.5-slim-buster

WORKDIR /app

COPY pyproject.toml .

RUN pip install poetry && poetry config virtualenvs.create false && poetry install --no-dev

COPY . .

#########################################

FROM nginx:1.19.2

RUN rm -v /etc/nginx/nginx.conf
ADD ./nginx/nginx.conf /etc/nginx/
