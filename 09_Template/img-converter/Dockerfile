FROM ghcr.io/withlogicco/poetry:1.7.1-python-3.12

WORKDIR /app
COPY poetry.lock pyproject.toml ./

RUN poetry install --no-interaction --no-cache --no-root

COPY .. .
CMD ["poetry", "run", "python", "app.py"]
