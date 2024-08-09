# Use the official Python image from the Docker Hub
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /jobs

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . /jobs/

ENV URL_POKE_ORDER_API=http://poke-order-api:8000/orders

CMD ["python", "app/main.py"]