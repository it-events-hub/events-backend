FROM python:3.10-slim
RUN pip install "poetry==1.6.1"
WORKDIR /app
COPY poetry.lock pyproject.toml /app/
RUN poetry config virtualenvs.create false \
  && poetry install --without dev --no-interaction --no-root
COPY src/ /app/
