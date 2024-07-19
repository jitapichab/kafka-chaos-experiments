import os


class Config:
    bootstrap_servers = os.getenv('KAFKA_BOOTSTRAP_SERVERS',
                                  'localhost:9092')
    producer_client_id = os.getenv('PRODUCER_CLIENT_ID', 'poke-producer')
    producer_topic = os.getenv('PRODUCER_TOPIC', 'poke-orders-state')
    consumer_group_id = os.getenv('CONSUMER_GROUP_ID', 'poke-order-consumer')
    consumer_topic = os.getenv('CONSUMER_TOPIC', 'orders')