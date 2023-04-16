#!/usr/bin/env python3
from kafka import KafkaConsumer
from kafka.structs import TopicPartition
from json import loads, dump
import time
import os, sys

def get_script_path():
    return os.path.dirname(os.path.realpath(sys.argv[0]))


def main(TAG, verbose=False):
    consumer = KafkaConsumer(
        bootstrap_servers=['localhost:9092'],
        auto_offset_reset='latest',
        enable_auto_commit=True,
        group_id='online-odb',
        value_deserializer=lambda x: loads(x.decode('utf-8'))
    )

    fpath = get_script_path()
    consumer.subscribe('midas-odb-'+TAG)
    
    while True:
        try:
            for message in consumer:
                odb = loads(message.value)
                with open(fpath+'/'+TAG+'_odb.json', 'w', encoding='utf-8') as f:
                    dump(odb, f, ensure_ascii=False, indent=4)
                if verbose:
                    topic_info = f"topic: {message.partition}|{message.offset})"
                    message_info = f"key: {message.key}, {message.value}"
                    print(f"{topic_info}, {message_info}")
                    value = odb["Runinfo"]
                    for key in value:
                        print(key, "->", value[key])
        except Exception as e:
            print(f"Error occurred while consuming messages: {e}")
            sys.exit(1)
        except KeyboardInterrupt:
            sys.exit(0)
            consumer.close()
    

        time.sleep(0.1)

    
if __name__ == "__main__":
    from optparse import OptionParser
    parser = OptionParser(usage='usage: %prog\t ')
    parser.add_option('-t','--tag', dest='tag', type='string', default='LNGS', help='tag LNF/LNGS [LNGS];');
    parser.add_option('-v','--verbose', dest='verbose', action="store_true", default=False, help='verbose output;');
    (options, args) = parser.parse_args()
    main(TAG=options.tag, verbose=options.verbose)