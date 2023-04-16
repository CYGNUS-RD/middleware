#!/bin/python3

from kafka import KafkaProducer
from kafka.errors import KafkaError
import os
import base64
import io
import json
import time

datapath = "./test_data/"
data_payload = os.listdir(datapath)
data_payload = sorted(data_payload)

producer = KafkaProducer(
    bootstrap_servers = "localhost:9092",
    max_request_size  = 31457280,
#    compression_type  = 'gzip',
    max_block_ms      = 300000
)

topic = "welcome"

def on_success(metadata):
    print(f"Message produced to topic '{metadata.topic}' at offset {metadata.offset}")

def on_error(e):
    print(f"Error sending message: {e}")

# Produce asynchronously with callbacks


for i, payload in enumerate(data_payload):
    t1 = time.time()
#    with open(datapath+payload, 'rb') as f:
#        data_bytes = f.read()
    with open('/tmp/payload.dat', 'rb') as f:
         data_bytes = f.read()

    data_base64 = base64.b64encode(data_bytes).decode('utf-8')
    t2  = time.time()
    future = producer.send(topic, value=data_base64.encode('utf-8'))
    future.add_callback(on_success)
    future.add_errback(on_error)
    t3 = time.time()
    del data_bytes, data_base64
    producer.flush()
    t4 = time.time()
    print("{:d} {:} read and decode: {:.2f} send: {:.2f} flush {:.2f}".format(i, payload, t2-t1, t3-t2, t4-t3))

producer.close()
