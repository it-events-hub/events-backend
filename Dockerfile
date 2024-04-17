FROM python:3.10-slim
# prevent python from writing .pyc files
ENV PYTHONUNBUFFERED 1
# ensure python output is sent directly to the terminal without buffering
ENV PYTHONDONTWRITEBYTECODE 1
RUN pip install "poetry==1.6.1"
WORKDIR /app
COPY poetry.lock pyproject.toml /app/
RUN poetry config virtualenvs.create false \
  && poetry install --without dev --no-interaction --no-root
COPY src/ /app/
