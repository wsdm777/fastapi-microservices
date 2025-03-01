FROM python:3.12.8-slim

WORKDIR /app

RUN pip install --no-cache-dir asyncpg==0.30.0

COPY . .

CMD ["python", "create_schemas.py"]