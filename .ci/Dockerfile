FROM python:3.9-slim

ENV POETRY_HOME /opt/poetry
ENV POETRY_VIRTUALENVS_CREATE false

ENV ANSIBLE_HOST_KEY_CHECKING false


RUN apt-get update -qq && \
    apt-get install -yqq curl ssh && \
    rm -rf /var/lib/apt/lists/* && \
    apt-get -qq clean


# Install poetry
RUN pip install --target=$POETRY_HOME --no-cache-dir poetry


# Intall plugin
WORKDIR /plugin

COPY src /plugin/src/
COPY pyproject.toml poetry.lock /plugin/

RUN PYTHONPATH=$POETRY_HOME $POETRY_HOME/bin/poetry install --no-dev --no-interaction && rm -rf $POETRY_HOME


ENTRYPOINT ["socks5-tune"]
