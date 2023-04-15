#!/bin/python3
from kafka import KafkaConsumer

consumer = KafkaConsumer(
  bootstrap_servers=["localhost:42461"],
  group_id="demo-group",
  auto_offset_reset="earliest",
  enable_auto_commit=False,
  consumer_timeout_ms=1000
)

consumer.subscribe("welcome")

try:
    for message in consumer:
        topic_info = f"topic: {message.partition}|{message.offset})"
        message_info = f"key: {message.key}, {message.value}"
        #print(f"{topic_info}, {message_info}")
        print(f"{topic_info}")
except Exception as e:
    print(f"Error occurred while consuming messages: {e}")
finally:
    consumer.close()
