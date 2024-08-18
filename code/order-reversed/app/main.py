import psycopg2
from psycopg2 import sql

from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime, timedelta

from yunopyutils import build_logger

from config import Config

_LOGGER = build_logger(__name__)


class Worker:

    def __init__(self):
        self.db_host = Config.db_host
        self.db_port = Config.db_port
        self.db_user = Config.db_user
        self.db_password = Config.db_password
        self.db_name = Config.db_name
        self.expired_order_time = Config.expired_order_time

    def run_tasks(self):
        try:
            connection = psycopg2.connect(
                dbname=self.db_name,
                user=self.db_user,
                password=self.db_password,
                host=self.db_host,
                port=self.db_port
            )
            cursor = connection.cursor()

            threshold_time = datetime.now() - timedelta(
                minutes=self.expired_order_time)

            update_query = sql.SQL("""
                UPDATE poke_orders
                SET state = 'reversed'
                WHERE state = 'pending'
                AND timestamp < %s
            """)

            cursor.execute(update_query, [threshold_time])

            connection.commit()

            _LOGGER.info(
                f"{cursor.rowcount} orders were updated to 'reversed'."
                )

        except (Exception, psycopg2.DatabaseError) as error:
            _LOGGER.error(f"Error: {error}")
        finally:
            if connection is not None:
                cursor.close()
                connection.close()

    def run_worker(self):
        scheduler = BlockingScheduler()
        scheduler.add_job(self.run_tasks, "interval",
                          minutes=1,
                          next_run_time=datetime.now() + timedelta(seconds=1))
        _LOGGER.info("Initializing order-reversed orders!")
        scheduler.start()


if __name__ == "__main__":
    worker = Worker()
    worker.run_worker()
