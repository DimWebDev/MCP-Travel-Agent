# File: app/mcp_servers/trivia/Dockerfile

FROM python:3.11-slim

WORKDIR /app

# Install runtime dependencies using Poetry
COPY ../../../pyproject.toml /app/
RUN pip install --no-cache-dir poetry \
    && poetry config virtualenvs.create false \
    && poetry install --only main --no-interaction --no-ansi

COPY ../../../app /app/app

CMD ["python", "-m", "app.mcp_servers.trivia.server"]
