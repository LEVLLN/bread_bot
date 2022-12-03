FROM python:3.11.0

WORKDIR /code

COPY . /code/

RUN pip install poetry && poetry config virtualenvs.create false && poetry install --only main