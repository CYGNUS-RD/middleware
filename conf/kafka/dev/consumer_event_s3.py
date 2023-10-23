#!/usr/bin/env python3
from kafka import KafkaConsumer
import time
from datetime import datetime
import numpy as np

from midas import event
import midas

import cygno as cy

import io, sys, json, os
import requests
import boto3
from boto3sts import credentials as creds

baseurl = "https://s3.cloud.infn.it/v1/AUTH_2ebf769785574195bde2ff418deac08a/cygno-data/EVENTS/"

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

def main(TAG, session, verbose=False):
    vmin         = 95
    vmax         = 130
    connection   =-1
    attempts     = 0

    consumer = KafkaConsumer(
        bootstrap_servers=["localhost:9092"],
        group_id="demo-group",
        auto_offset_reset="earliest",
        enable_auto_commit=True,
        fetch_max_bytes = 31457280,
        max_partition_fetch_bytes = 31457280,
        consumer_timeout_ms=1000

    )
    while attempts < 3:
        try:
            session = creds.assumed_session(session, endpoint="https://minio.cloud.infn.it/", verify=True)
            s3 = session.client('s3', endpoint_url="https://minio.cloud.infn.it/",
                                config=boto3.session.Config(signature_version='s3v4'),
                                verify=True)
            attempts = 0
            break
        except Exception as e:
            attempts += 1
            print("error opening client session:",  attempts, e)
            time.sleep(10)
            
    topic = 'midas-event-file-'+TAG
    #
    # reset to the end of the stream
    # consumer.poll()
    # consumer.seek_to_end()
    #
    event = midas.event.Event()
    consumer.subscribe(topic)
    start = time.time()
    
    while True:
        try:
            for mes in consumer:
                t1 = time.time()
                event_info_json = json.loads(json.loads(mes.value))

                # if verbose:
                #     print(event_info_json)
                
                payload_name =  "{}_{}_{}.dat".format(TAG, event_info_json["timestamp"], event_info_json["serial_number"])

                url = baseurl+payload_name 
                response = requests.get(url)
                
                if verbose:
                    print(payload_name, response.status_code)
                    
                if response.status_code==200:
                    payload = response.content

                    event.unpack(payload, use_numpy=False)
                    bank_names = ", ".join(b.name for b in event.banks.values())

                    bank_names    = ", ".join(b.name for b in event.banks.values())
                    event_info    = [event.header.timestamp, event.header.serial_number, event.header.event_id]
                    event_number  = event.header.serial_number
                    event_time    = datetime.fromtimestamp(event.header.timestamp).strftime('%Y-%m-%d %H:%M:%S')
                    end = time.time()
                    if verbose: print (event_info, bank_names)
                    if ('CAM0' in bank_names) and (end-start)>10:
                        # ora bypassato serviva solo per vedere che fosse creato quello che serviva
                        # image, _, _ = cy.daq_cam2array(event.banks['CAM0']) # matrice delle imagine
                        # image_jpg(image, vmin, vmax, event_number, event_time)
                        if (verbose):
                            print(">>> GENERATING jpeg IMAGE")
                        start = time.time()
                    while attempts < 3:
                        try:
                            s3.delete_object(Bucket='cygno-data', Key='EVENTS/'+payload_name)
                            if verbose: print ("delete file")
                            attempts = 0
                            break
                        except Exception as e:
                            attempts += 1
                            print("error removing object:",  attempts, e)
                            time.sleep(10)
                    #cy.s3.obj_rm(payload_name, TAG, bucket='cygno-data', session=session, verbose=verbose)
                # if verbose:
                #     topic_info = f"topic: {mes.partition}|{mes.offset})"
                #     mes_info = f"key: {mes.key}, {mes.value}"
                #     print(f"{topic_info}")

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
    parser.add_option('-s','--session', dest='session', type='string', default='sentinel-wlcg', help='session [sentinel-wlcg];');
    parser.add_option('-v','--verbose', dest='verbose', action="store_true", default=False, help='verbose output;');
    (options, args) = parser.parse_args()
    main(TAG=options.tag, session=options.session, verbose=options.verbose)
