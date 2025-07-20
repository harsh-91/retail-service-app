from kafka import KafkaProducer
import json
import os

producer = KafkaProducer(
    bootstrap_servers=[os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

def emit_event(topic: str, event: dict):
    # Best effort: Errors should not crash main sale flow!
    try:
        producer.send(topic, event)
        producer.flush(timeout=1)
    except Exception as e:
        print(f"Error emitting Kafka event on {topic}: {e}")
