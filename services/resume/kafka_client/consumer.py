import asyncio
import contextlib
import json
import logging
from typing import Any, Callable, Dict

from aiokafka import AIOKafkaConsumer, ConsumerRecord
from pydantic import BaseModel

from middleware import current_user_id_ctx_var, request_id_ctx_var
from kafka_client.schemas import UserDeleteEvent
from resume.service import ResumeService

logger = logging.getLogger(__name__)

TOPICS = ["user.delete", "resume.create"]

resume_service = ResumeService()


async def handle_user_delete(event: UserDeleteEvent):
    request_id_ctx_var.set(event.request_id)
    current_user_id_ctx_var.set(event.deleter_id)

    logger.info("Handle user delete message from kafka")
    await resume_service.delete_user_resumes(event.deleted_user_id)


TOPIC_HANDLERS: Dict[str, tuple[type[BaseModel], Callable]] = {
    "user.delete": (UserDeleteEvent, handle_user_delete),
}

consumer: AIOKafkaConsumer | None = None
consumer_task: asyncio.Task | None = None


async def _consume():
    global consumer
    consumer = AIOKafkaConsumer(
        *TOPICS,
        bootstrap_servers="kafka:9092",
        group_id="resume-service",
        value_deserializer=lambda v: json.loads(v.decode("utf-8")),
        auto_offset_reset="earliest",
    )
    await consumer.start()
    try:
        async for msg in consumer:
            topic = msg.topic
            value = msg.value
            if value is None:
                logger.warning(f"Пустое сообщение из топика {topic}")
                continue
            if topic in TOPIC_HANDLERS:
                model_cls, handler = TOPIC_HANDLERS[topic]
                try:
                    data: dict[str, Any] = value
                    event = model_cls(**data)
                    await handler(event)
                except Exception as e:
                    logger.exception(f"Ошибка обработки {topic}: {e}")
    finally:
        await consumer.stop()


async def start_kafka_consumer():
    global consumer_task
    consumer_task = asyncio.create_task(_consume())


async def stop_kafka_consumer():
    global consumer_task
    if consumer_task:
        consumer_task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await consumer_task
