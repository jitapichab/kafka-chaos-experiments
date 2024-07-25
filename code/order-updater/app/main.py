from time import sleep
from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime, timedelta
from yunopyutils import build_logger
import json
import requests


from config import Config

from confluent_kafka import (
    Consumer,
    KafkaException,
    KafkaError,
    TopicPartition
)

_LOGGER = build_logger(__name__)


class Worker:

    def __init__(self):
        self.bootstrap_server = Config.bootstrap_servers
        self.consumer_group_id = Config.consumer_group_id
        self.consumer_topic = Config.consumer_topic
        self.url_poke_order_api = Config.url_poke_order_api

    def config_consumer(self):
        conf = {
            "bootstrap.servers": self.bootstrap_server,
            "group.id": self.consumer_group_id,
            "auto.offset.reset": "earliest",
            "enable.auto.commit": False,
        }
        return Consumer(conf)
    
    

    def update_order_state(self, order_id, state):
        url = f'{self.url_poke_order_api}/{order_id}'
        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json'
        }
        data = {
            'state': state
        }
        try:
            response = requests.put(url, headers=headers, json=data)
            response.raise_for_status()
            if response.status_code == 200:
                _LOGGER.info(f"Order {order_id} state updated"
                             f" with state: {state}")
                return response.json()
        except Exception as req_err:
            raise Exception(f'Error occurred: {req_err}') from req_err

    def run_tasks(self):
        _LOGGER.info("Running tasks")
        consumer = self.config_consumer()

        consumer.subscribe([self.consumer_topic])

        while True:
            try:
                msg = consumer.poll(timeout=1.0)

                if msg is None:
                    continue

                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        _LOGGER.info(
                            f"End of partition reached : {msg.topic()}"
                            f"{msg.partition()}, {msg.offset()}"
                        )
                    elif msg.error():
                        raise KafkaException(msg.error())
                else:
                    order = json.loads(msg.value().decode("utf-8"))
                    _LOGGER.info(f"Consumed message: {order}")
                    order_id = order.get('id')
                    state = order.get('state')
                    self.update_order_state(order_id, state)
                    consumer.commit(msg)
            except Exception as error:
                _LOGGER.info(f"Error processing message {msg.value()}"
                             f"with error: {error}")
                sleep(5)
                current_offset = consumer.committed(
                    [TopicPartition(msg.topic(), msg.partition())]
                )[0].offset
                consumer.seek(
                    TopicPartition(msg.topic(),
                                   msg.partition(),
                                   current_offset)
                )

    def run_worker(self):
        scheduler = BlockingScheduler()
        scheduler.add_job(self.run_tasks, "interval", seconds=30,
                          next_run_time=datetime.now() + timedelta(seconds=1))
        _LOGGER.info("Initializing order-updater worker!")
        scheduler.start()


if __name__ == "__main__":
    worker = Worker()
    worker.run_worker()
