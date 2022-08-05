FROM python:3.9.4-slim AS server

WORKDIR /server

COPY ./pyproject.toml /server/
COPY ./poetry.lock /server/

RUN pip install poetry && poetry config virtualenvs.create false && poetry install --no-dev

COPY ./src /server

#########################################

FROM nginx:1.19.2

RUN rm -v /etc/nginx/nginx.conf
ADD ./nginx/nginx.conf /etc/nginx/
