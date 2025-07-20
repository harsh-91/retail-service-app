import asyncio
import json
from aiokafka import AIOKafkaConsumer
from analytics_db import db
from models import DomainEvent
from datetime import datetime
import os
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
EVENT_TOPICS = [
    'sale.created', 'payment.received', 'inventory.updated',
    'gst.invoice.generated', 'notification.sent'
]

async def store_event(event: DomainEvent):
    coll = db.domain_events
    await coll.insert_one(event.dict())

async def consume_events():
    consumer = AIOKafkaConsumer(
        *EVENT_TOPICS,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        group_id="analytics_service"
    )
    await consumer.start()
    try:
        async for msg in consumer:
            raw = json.loads(msg.value)
            event = DomainEvent(
                event_type=raw['event_type'],
                tenant_id=raw['tenant_id'],
                payload=raw['payload'],
                timestamp=raw.get('timestamp', datetime.utcnow())
            )
            await store_event(event)
    finally:
        await consumer.stop()
