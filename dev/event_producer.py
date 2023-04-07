#!/usr/bin/env python3
#
# I. Abritta and G. Mazzitelli March 2022
# Middelware online recostruction 
# Modify by ... in date ...
#

import os, sys

# Load globals env
DAQ_ROOT            = os.environ['DAQ_ROOT']
DEFAULT_PATH_ONLINE = DAQ_ROOT+'/online/'
TAG                 = os.environ['TAG']

def image_jpg(image, vmin, vmax, event_number, event_time):
    from matplotlib import pyplot as plt
    im = plt.imshow(image, cmap='gray', vmin=vmin, vmax=vmax)
    plt.title ("Event: {:d} at {:s}".format(event_number, event_time))
    plt.savefig(DEFAULT_PATH_ONLINE+'custom/tmp.png')
    return 

def main(verbose=True):
    import numpy as np

    from datetime import datetime

    import time
    import base64
    import json

    import midas
    import midas.client

    import mysql.connector

    import cygno as cy

    from json import dumps
    from kafka import KafkaProducer
    import subprocess
    
    producer = KafkaProducer(
        bootstrap_servers=['localhost:9092'],
        value_serializer=lambda x: dumps(x).encode('utf-8')
    )    
    
    client = midas.client.MidasClient("middleware")
    buffer_handle = client.open_event_buffer("SYSTEM",None,1000000000)
    request_id = client.register_event_request(buffer_handle, sampling_type = 2) 
    
    # init program variables #####
    vmin         = 95
    vmax         = 130
    odb_update   = 3 # probabilemnte da mettere in middleware 
    event_info   = {}
    end1 = time.time()
    
    
    while True:
        start1 = time.time()
        if (start1-end1) > odb_update:
            # update ODB
            odb_json = dumps(client.odb_get("/"))
            producer.send('midas-odb-'+TAG, value=odb_json)
            end1 = time.time()
            print("ODB elapsed: {:.2f}, payload size {:.1f} kb".format(end1-start1, len(odb_json.encode('utf-8'))/1024))
            # ######
            
        start2 = time.time()
        event = client.receive_event(buffer_handle, async_flag=True)
        if event is not None:
            if event.header.is_midas_internal_event():
                if verbose:
                    print("Saw a special event")
                continue
                
            # load global event useful variables from header
            bank_names    = ", ".join(b.name for b in event.banks.values())
            event_number  = event.header.serial_number
            event_time    = datetime.fromtimestamp(event.header.timestamp).strftime('%Y-%m-%d %H:%M:%S')
            run_number    = client.odb_get("/Runinfo/Run number")
            event_info["timestamp"]             = event.header.timestamp
            event_info["serial_number"]         = event.header.serial_number
            event_info["event_id"]              = event.header.event_id
            event_info["trigger_mask"]          = event.header.trigger_mask
            event_info["event_data_size_bytes"] = event.header.event_data_size_bytes
            event_info["run_number"]            = run_number
            event_info_json = dumps(event_info)
            # #################
            # update EVENT
            payload = event.pack()

            binary_data = io.BytesIO()
            binary_data.write(payload)
            binary_data.seek(0)
            encoded_data = binary_data.read()
            
            producerb.send('midas-event'+TAG, value=(encoded_data))
            producerb.flush()

            end2 = time.time()
            if verbose: print("EVENT elapsed: {:.2f}, payload size {:.1f} Mb, timestamp {:} ".format(end2-start2, np.size(payload)/1024/1024, event.header.timestamp))

            image_update_time = client.odb_get("/middleware/image_update_time")
            if ('CAM0' in bank_names) and (int(time.time())%image_update_time==0): # CAM image
                image, _, _ = cy.daq_cam2array(event.banks['CAM0']) # matrice delle imagine
                image_jpg(image, vmin, vmax, event_number, event_time)

              
        client.communicate(10)
        time.sleep(0.1)
        

    client.deregister_event_request(buffer_handle, request_id)

    client.disconnect()
    
        
if __name__ == "__main__":
    from optparse import OptionParser
    parser = OptionParser(usage='usage: %prog\t ')
    parser.add_option('-v','--verbose', dest='verbose', action="store_true", default=False, help='verbose output;');
    (options, args) = parser.parse_args()
    main(verbose=options.verbose)
