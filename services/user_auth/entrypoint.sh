#!/bin/sh
echo "Running migrations"
poetry run alembic upgrade head

UVICORN_WORKERS=${UVICORN_WORKERS:-1}

echo "Starting application with $UVICORN_WORKERS workers..."
exec poetry run gunicorn main:app --workers "$UVICORN_WORKERS" --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000