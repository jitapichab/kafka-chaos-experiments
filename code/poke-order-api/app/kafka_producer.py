from confluent_kafka import Producer
from yunopyutils import build_logger
import json
import os

from .config import Config

_LOGGER = build_logger(__name__)

KAFKA_BOOTSTRAP_SERVERS = Config.KAFKA_BOOTSTRAP_SERVERS
KAFKA_CLIENT_ID = Config.KAFKA_CLIENT_ID
KAFKA_ACKS = Config.KAFKA_ACKS
RETRIES = Config.RETRIES
TOPIC = Config.KAFKA_TOPIC


KAFKA_CONFIG = {
    'bootstrap.servers': KAFKA_BOOTSTRAP_SERVERS,
    'client.id': KAFKA_CLIENT_ID,
    'acks': KAFKA_ACKS,
    'retries': RETRIES
}

producer = Producer(KAFKA_CONFIG)


def delivery_callback(err, msg):
    if err is not None:
        _LOGGER.info(f"Message delivery failed: {err}")
    else:
        _LOGGER.info(f"Message delivered to {msg.topic()} [{msg.partition()}]")


def produce_order_message(order):
    message = json.dumps(order, default=str)
    producer.produce(TOPIC, message.encode('utf-8'),
                     callback=delivery_callback)
    producer.flush()