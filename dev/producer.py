#!/usr/bin/env python3
from time import sleep
from json import dumps
from kafka import KafkaProducer
import time
import numpy as np
producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    max_request_size= 31457280,
    value_serializer=lambda x: dumps(x).encode('utf-8')
)
data_file = []
for j in range(110):
    # print("Iteration", j)
    
    aux = np.ones([1,100*1024*j]).tolist()
    data = {'counter': aux}
    start = time.time()
    producer.send('topic_test', value=data)
    producer.flush()
    stop = time.time()
    print("event {:d}, size: {:.2f} Mb, time: {:.2f} s".format(j, np.size(aux)/1024/1024, stop-start))
    data_file.append([j, np.size(aux)/1024/1024, stop-start])
#    sleep(0.1)
np.save("data.npy", data_file)