#!/usr/bin/env python3
#
# I. Abritta and G. Mazzitelli March 2022
# Middelware online recostruction 
# Modify by ... in date ...
#
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
    import os, sys
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
    t0 = time.time()
    vmin         = 95
    vmax         = 130

    
    while True:
        start = time.time()
        event = client.receive_event(buffer_handle, async_flag=True)
        # update ODB
        odb_json = dumps(client.odb_get("/"))
        producer.send('midas-odb-'+TAG, value=odb_json)
        end = time.time()
        print("ODB elapsed: {:.2f}, payload size {:.1f} kb".format(end-start, len(odb_json.encode('utf-8'))/1024))
        # ######
        start = time.time()
        
        if event is not None:
            if event.header.is_midas_internal_event():
                if verbose:
                    print("Saw a special event")
                continue
                
            # load global event useful variables from header
            bank_names    = ", ".join(b.name for b in event.banks.values())
            event_info    = [event.header.timestamp, event.header.serial_number, event.header.event_id]
            event_number  = event.header.serial_number
            event_time    = datetime.fromtimestamp(event.header.timestamp).strftime('%Y-%m-%d %H:%M:%S')
            # #################
            # update EVENT
            payload = event.pack()
            payload_name =  "/tmp/{}_{}.dat".format(TAG, event.header.timestamp)
            with open(payload_name, "wb") as f:
                f.write(payload)
            command = "scp -i /home/standard/.ssh/daq_id "+payload_name+" mazzitel@131.154.96.175:/tmp/ && rm "+payload_name
            status, output = subprocess.getstatusoutput(command)
            event_info_json = dumps(event_info)
            end = time.time()
            if status==0:
                producer.send('midas-event-file-'+TAG, value=event_info_json)
                
                if verbose: print("EVENT elapsed: {:.2f}, payload size {:.1f} Mb encoded {:.1f} Mb timestamp {:} ".format(end-start, np.size(payload)/1024/1024, np.size(encoded_data)/1024/1024, event.header.timestamp))
            else:
                print(event_time+": ERROR in coping event")

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
