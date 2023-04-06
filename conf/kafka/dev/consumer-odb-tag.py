#!/usr/bin/env python3
from kafka import KafkaConsumer
from kafka.structs import TopicPartition
from json import loads, dump
import time
import os, sys
TAG='LNGS'
def get_script_path():
    return os.path.dirname(os.path.realpath(sys.argv[0]))

consumer = KafkaConsumer(
    'midas-odb-'+TAG,
    bootstrap_servers=['localhost:9092'],
    auto_offset_reset='latest',
    enable_auto_commit=True,
    group_id='online-odb',
    value_deserializer=lambda x: loads(x.decode('utf-8'))
)
# reset to the end of the stream

# consumer.subscribe('midas-odb')
# partition = TopicPartition('midas-odb', 0)
# #end_offset = consumer.end_offsets([partition])
# consumer.seek_to_end(partition)

start = time.time()
fpath = get_script_path()
for event in consumer:
    event_data = event.value
    odb = loads(event_data)
    end = time.time()
    if int(end-start)>2: # write no faster then value
        # print ("DT: {} run {} Event: {}".format(int(end-start), odb["Runinfo"]["Run number"],
        #                                         odb["Equipment"]["Trigger"]["Statistics"]))
        start = time.time()
        # dump info
        value = odb["Runinfo"]
        for key in value:
            print(key, "->", value[key])

        with open(fpath+'/odb.json', 'w', encoding='utf-8') as f:
            dump(odb, f, ensure_ascii=False, indent=4)

    time.sleep(0.1)
