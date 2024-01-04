#!/usr/bin/env python3
from kafka import KafkaConsumer
from kafka.structs import TopicPartition
from json import loads, dump, load
import time
import os, sys
import pymongo

def get_script_path():
    return os.path.dirname(os.path.realpath(sys.argv[0]))


def main(kafka_ip, tag, mongo, verbose=False):
    consumer = KafkaConsumer(
        bootstrap_servers=[kafka_ip],
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
    consumer.subscribe(['midas-odb-'+tag, 'midas-camera-'+tag, 'midas-pmt-s'+tag, 'midas-pmt-f'+tag])
    start_mongo = time.time()
    alive_time  = time.time()
    up_time_mongo = 600
    fpath = get_script_path()
    while True:
        
        try:
            raw_messages = consumer.poll(
                timeout_ms=100, max_records=1
            )
            for topic_partition, messages in raw_messages.items():
                end = time.time()
                if topic_partition.topic == 'midas-odb-'+tag:
                    if verbose:
                        print("DEBUG: odb")

                    odb = loads(messages[0].value)
                    odb["middleware_alive"] = 1
                    alive_time  = time.time()
                    with open(fpath+'/'+tag+'_odb.json', 'w', encoding='utf-8') as f:
                        dump(odb, f, ensure_ascii=False, indent=4)

                    if (end-start_mongo)>up_time_mongo and mongo:
                        mongo_col.insert_one(odb)
                        start_mongo = time.time()
                        
                elif topic_partition.topic == 'midas-camera-'+tag:
                    if verbose:
                        print("DEBUG: camera")

                    img_base64 = messages[0].value#.decode('utf-8')
                    data = {'image': img_base64}
                    # write json to file
                    with open(fpath+'/'+tag+'_image.json', 'w') as f:
                        dump(data, f)
                elif topic_partition.topic == 'midas-pmt-f'+tag:
                    if verbose:
                        print("DEBUG: pmt")
                    img_base64 = messages[0].value#.decode('utf-8')
                    data = {'image': img_base64}
                    # write json to file
                    with open(fpath+'/'+tag+'_pmt_f.json', 'w') as f:
                        dump(data, f)
                elif topic_partition.topic == 'midas-pmt-s'+tag:
                    if verbose:
                        print("DEBUG: pmt")
                    img_base64 = messages[0].value#.decode('utf-8')
                    data = {'image': img_base64}
                    # write json to file
                    with open(fpath+'/'+tag+'_pmt_s.json', 'w') as f:
                        dump(data, f)
        except Exception as e:
            print(f"Error occurred while consuming messages: {e}")
            sys.exit(1)
        except KeyboardInterrupt:
            consumer.close()
            if mongo:
                mongo_client.close()
            sys.exit(0)

        if (time.time()-alive_time)>10:
            if verbose:
                print("DEBUG: >>> dead")
            with open(fpath+'/'+tag+'_odb.json', 'r') as f:
                odb = load(f)
            odb["middleware_alive"] = 0
            with open(fpath+'/'+tag+'_odb.json', 'w', encoding='utf-8') as f:
                dump(odb, f, ensure_ascii=False, indent=4)
            time.sleep(3)

    
if __name__ == "__main__":
    from optparse import OptionParser
    parser = OptionParser(usage='usage: %prog\t ')
    parser.add_option('-t','--tag', dest='tag', type='string', default='LNGS', help='tag LNF/LNGS [LNGS];');
    parser.add_option('-m','--mongo', dest='mongo', action="store_true", default=False, help='store in mongo ;');
    parser.add_option('-v','--verbose', dest='verbose', action="store_true", default=False, help='verbose output;');
    (options, args) = parser.parse_args()
    if len(args)<1:
        parser.print_help()
        exit(1) 
    main(args[0], tag=options.tag, mongo=options.mongo, verbose=options.verbose)
