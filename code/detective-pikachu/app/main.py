from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime, timedelta
from yunopyutils import build_logger
import json


from config import Config

from confluent_kafka import (
    Consumer,
    Producer,
    KafkaException,
    KafkaError,
    TopicPartition,
)

_LOGGER = build_logger(__name__)


def fraud_rules(order):
    if order["price"] > 200:
        return True
    if order["user_id"] == 5:
        return True
    return bool(order["pokemon"].startswith(("d", "f", "a")))


def delivery_callback(err, msg):
    if err is not None:
        _LOGGER.info(f"Message delivery failed: {err}")
        raise ("Message delivery failed")
    else:
        _LOGGER.info(f"Message delivered to {msg.topic()} [{msg.partition()}]")


class Worker:

    def __init__(self):
        self.bootstrap_server = Config.bootstrap_servers
        self.consumer_group_id = Config.consumer_group_id
        self.consumer_topic = Config.consumer_topic
        self.produce_topic = Config.producer_topic
        self.producer_client_id = Config.producer_client_id

    def config_consumer(self):
        conf = {
            "bootstrap.servers": self.bootstrap_server,
            "group.id": self.consumer_group_id,
            "auto.offset.reset": "earliest",
            "enable.auto.commit": False,
        }
        return Consumer(conf)

    def config_producer(self):
        conf = {
            "bootstrap.servers": self.bootstrap_server,
            "client.id": self.producer_client_id,
            "acks": "all",
            "retries": 3,
        }
        return Producer(conf)

    def run_tasks(self):
        _LOGGER.info("Running tasks")
        consumer = self.config_consumer()
        producer = self.config_producer()

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
                    order["state"] = (
                        "rejected" if fraud_rules(order) else "success"
                    )
                    producer.produce(
                        self.produce_topic,
                        json.dumps(order).encode("utf-8"),
                        callback=delivery_callback,
                    )
                    producer.flush()
                    consumer.commit(msg)
            except Exception:
                _LOGGER.info(f"Error processing message {msg.value()}")
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
        _LOGGER.info("Initializing pikachu worker detective!")
        scheduler.start()


if __name__ == "__main__":
    worker = Worker()
    worker.run_worker()
