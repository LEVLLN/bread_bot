FROM python:3.10.5

WORKDIR /code

COPY . /code/

RUN pip install poetry && poetry install --only main
