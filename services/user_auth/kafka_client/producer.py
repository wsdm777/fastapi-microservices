import logging
from aiokafka import AIOKafkaProducer
from kafka_client.schemas import UserDeleteEvent
from config import KAFKA_URL

producer: AIOKafkaProducer | None = None

logger = logging.getLogger(__name__)


async def init_kafka_producer():
    global producer
    producer = AIOKafkaProducer(bootstrap_servers=KAFKA_URL)
    await producer.start()


async def stop_kafka_producer():
    global producer
    if producer:
        await producer.stop()
        producer = None


async def produce_user_delete_event(event: UserDeleteEvent):
    if not producer:
        raise RuntimeError("Kafka producer is not initialized")

    value = event.model_dump_json().encode("utf-8")

    await producer.send_and_wait("user.delete", value)
