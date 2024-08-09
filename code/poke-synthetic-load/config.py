import os


class Config:
    bootstrap_servers = os.getenv('KAFKA_BOOTSTRAP_SERVERS',
                                  'localhost:9092')
    consumer_group_id = os.getenv('CONSUMER_GROUP_ID', 'order-updater')
    consumer_topic = os.getenv('CONSUMER_TOPIC', 'poke-orders-state')
    url_poke_order_api = os.getenv('URL_POKE_ORDER_API', 'http://localhost:8000/orders')