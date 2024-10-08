import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    DATABASE_URL = os.getenv(
        'DATABASE_URL',
        'postgresql+asyncpg://user:password@localhost:5433/poke_orders'
        )
    KAFKA_BOOTSTRAP_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS',
                                        'localhost:9092')
    KAFKA_TOPIC = os.getenv('KAFKA_TOPIC', 'poke-orders')
    KAFKA_CLIENT_ID = os.getenv('KAFKA_CLIENT_ID', 'poke-producer')
    KAFKA_ACKS = os.getenv('KAFKA_ACKS', 'all')
    RETRIES = int(os.getenv('RETRIES', 3))
    MESSAGE_TIMEOUT_MS = os.getenv('MESSAGE_TIMEOUT_MS', 2000)
