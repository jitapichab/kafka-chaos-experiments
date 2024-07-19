FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV DATABASE_URL="postgresql+asyncpg://user:password@172.17.0.2:5432/poke_orders"
ENV KAFKA_BOOTSTRAP_SERVERS="localhost:9092"

EXPOSE 8000


CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"]