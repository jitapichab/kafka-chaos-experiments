FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y postgresql-client

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV DATABASE_URL="postgresql+asyncpg://user:password@postgres:5432/poke_orders"
ENV KAFKA_BOOTSTRAP_SERVERS="localhost:9092"
ENV KAFKA_TOPIC="poke-orders"

EXPOSE 8000


CMD ["sh", "-c", "./start.sh"]