# Use the official Python image from the Docker Hub
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

ENV KAFKA_BOOTSTRAP_SERVERS=localhost:9092
ENV PRODUCER_CLIENT_ID=poke-producer
ENV PRODUCER_TOPIC=poke-orders-state
ENV CONSUMER_GROUP_ID=poke-order-consumer
ENV CONSUMER_TOPIC=orders

# Run app.py when the container launches
CMD ["python", "app/main.py"]