FROM python:3.10.5-slim-buster

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONBUFFERED 1

COPY pyproject.toml .
COPY . .
RUN pip install poetry==1.1.13 && \
    poetry config virtualenvs.create false && \
    poetry install --no-dev --no-interaction --no-ansi

#########################################

FROM nginx:1.19.2

RUN rm -v /etc/nginx/nginx.conf
ADD ./nginx/nginx.conf /etc/nginx/

RUN mkdir /nginx
COPY ./nginx/index.html /var/www/html/
COPY ./nginx/url_cert.pem /nginx/url_cert.pem
COPY ./nginx/url_private.key /nginx/url_private.key