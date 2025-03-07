#!/usr/bin/env python3
from kafka import KafkaConsumer
from kafka.structs import TopicPartition
from json import loads, dump
import time
import os, sys
import pymongo

def get_script_path():
    return os.path.dirname(os.path.realpath(sys.argv[0]))


def main(TAG, mongo, verbose=False):
    consumer = KafkaConsumer(
        bootstrap_servers=['localhost:9092'],
        auto_offset_reset='latest',
        enable_auto_commit=True,
        group_id='online-odb',
        value_deserializer=lambda x: loads(x.decode('utf-8'))
    )

    if mongo:
        mongo_client = pymongo.MongoClient( 'localhost', username='root', password='example')
        mongo_db = mongo_client["daq"]
        mongo_col = mongo_db["odb"]  
        
    fpath = get_script_path()
    consumer.subscribe('midas-odb-'+TAG)
    start = time.time()
    while True:
        
        try:
            for message in consumer:
                end = time.time()
                odb = loads(message.value)
                with open(fpath+'/'+TAG+'_odb.json', 'w', encoding='utf-8') as f:
                    dump(odb, f, ensure_ascii=False, indent=4)

                if (end-start)>600 and mongo:
                    mongo_col.insert_one(odb)
                    start = time.time()
                    
                if verbose:
                    topic_info = f"topic: {message.partition}|{message.offset})"
                    message_info = f"key: {message.key}"#, {message.value}"
                    print(f"{topic_info}, {message_info}")
                # value = odb["Runinfo"]
                    # for key in value:
                    #      print(key, "->", value[key])
        except Exception as e:
            print(f"Error occurred while consuming messages: {e}")
            sys.exit(1)
        except KeyboardInterrupt:
            consumer.close()
            if mongo:
                mongo_client.close()
            sys.exit(0)
    

        time.sleep(0.1)

    
if __name__ == "__main__":
    from optparse import OptionParser
    parser = OptionParser(usage='usage: %prog\t ')
    parser.add_option('-t','--tag', dest='tag', type='string', default='LNGS', help='tag LNF/LNGS [LNGS];');
    parser.add_option('-m','--mongo', dest='mongo', action="store_true", default=False, help='store in mongo ;');
    parser.add_option('-v','--verbose', dest='verbose', action="store_true", default=False, help='verbose output;');
    (options, args) = parser.parse_args()
    main(TAG=options.tag, mongo=options.mongo, verbose=options.verbose)