#!/usr/bin/env python3
from kafka import KafkaConsumer
# from json import loads
from time import sleep
import numpy as np
import io
import numpy as np
import struct
#from json import loads, dumps, dump
from midas import event
import midas
import pandas as pd
import mysql.connector
from datetime import datetime

import cygno as cy

import os
import sys

def get_script_path():
    return os.path.dirname(os.path.realpath(sys.argv[0]))

def image_jpg(image, vmin, vmax, event_number, event_time):
    import base64
    from matplotlib import pyplot as plt
    import json
    # semmai fare qualcosa per salvare l'imgine in json
    im = plt.imshow(image, cmap='gray', vmin=vmin, vmax=vmax)
    plt.title ("Event: {:d} at {:s}".format(event_number, event_time))
    plt.savefig('/tmp/tmp.png')
    with open('/tmp/tmp.png', 'rb') as f:
        img_bytes = f.read()
    img_base64 = base64.b64encode(img_bytes).decode('utf-8')
    # create json object
    data = {'image': img_base64}

    # write json to file
    fpath = get_script_path()
    with open(fpath+'/plot.json', 'w') as f:
        json.dump(data, f)
        
    f.close()
    plt.close()
    del im, img_bytes, img_base64, data, image
        
    return 



def main(TAG, verbose=False):
    vmin         = 95
    vmax         = 130
    connection   =-1

    consumer = KafkaConsumer(
        bootstrap_servers=["localhost:9092"],
        group_id="demo-group",
        auto_offset_reset="earliest",
        enable_auto_commit=True,
        fetch_max_bytes = 31457280,
        max_partition_fetch_bytes = 31457280,
        consumer_timeout_ms=1000

    )
    topic = 'midas-event-'+TAG
    #
    # reset to the end of the stream
    # consumer.poll()
    # consumer.seek_to_end()
    #
    event = midas.event.Event()
    consumer.subscribe(topic)
    
    
    while True:
        try:
            for mes in consumer:
                binary_data = io.BytesIO(mes.value)
                decoded_data = binary_data.read()
                payload = decoded_data
                event.unpack(payload, use_numpy=False)
                bank_names = ", ".join(b.name for b in event.banks.values())

                bank_names    = ", ".join(b.name for b in event.banks.values())
                event_info    = [event.header.timestamp, event.header.serial_number, event.header.event_id]
                event_number  = event.header.serial_number
                event_time    = datetime.fromtimestamp(event.header.timestamp).strftime('%Y-%m-%d %H:%M:%S')
                if verbose: print (event_info, bank_names)
                if ('CAM0' in bank_names):
                    image, _, _ = cy.daq_cam2array(event.banks['CAM0']) # matrice delle imagine
                    image_jpg(image, vmin, vmax, event_number, event_time)

                if verbose:
                    topic_info = f"topic: {mes.partition}|{mes.offset})"
                    mes_info = f"key: {mes.key}, {mes.value}"
                    print(f"{topic_info}")

        except Exception as e:
            print(f"Error occurred while consuming messages: {e}")
            sys.exit(1)
        except KeyboardInterrupt:
            sys.exit(0)
            consumer.close()
        
        
                
        
if __name__ == "__main__":
    from optparse import OptionParser
    parser = OptionParser(usage='usage: %prog\t ')
    parser.add_option('-t','--tag', dest='tag', type='string', default='LNGS', help='tag LNF/LNGS [LNGS];');
    parser.add_option('-v','--verbose', dest='verbose', action="store_true", default=False, help='verbose output;');
    (options, args) = parser.parse_args()
    main(TAG=options.tag, verbose=options.verbose)
