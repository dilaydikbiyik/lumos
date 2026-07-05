# Lumos backend — FastAPI + Alembic (Python 3.12)
FROM python:3.12-slim

WORKDIR /app

# Install dependencies first (layer cache survives code changes)
COPY backend/requirements.txt backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt

COPY backend/ backend/
COPY alembic/ alembic/
COPY alembic.ini .

EXPOSE 8000

# Apply migrations, then start the API
CMD ["sh", "-c", "alembic upgrade head && uvicorn backend.main:app --host 0.0.0.0 --port 8000"]
