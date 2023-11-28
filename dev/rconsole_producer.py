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


def image_jpg(image, vmin, vmax, event_number, event_time, producer, verbose=False):
    from matplotlib import pyplot as plt
    import numpy as np
    import base64
    fig, ax = plt.subplots(figsize=(8,8))
    im = ax.imshow(image, vmin=vmin, vmax=vmax) #, cmap='gray'
    fig.colorbar(im, ax=ax, shrink=0.8)
    ax.set_title("Event: {:d} at {:s}".format(event_number, event_time))
    plt.savefig(DEFAULT_PATH_ONLINE+'custom/tmp.png', bbox_inches='tight')#, bbox_inches='tight'
    plt.close()

    with open(DEFAULT_PATH_ONLINE+'custom/tmp.png', 'rb') as f:
        img_bytes = f.read()
    f.close()
    img_base64 = base64.b64encode(img_bytes).decode('utf-8')
    producer.send('midas-camera-'+TAG, value=img_base64)#.encode('utf-8'))
    producer.flush()
    if verbose:
        print("CAMEARA Image produced")
    del im, img_bytes, img_base64, image
    return 

def pmt_jpg(header, waveform_f, waveform_s, producer, number_of_w_readed = 8, verbose=False):
    from matplotlib import pyplot as plt
    import numpy as np
    import base64
    q1 = min(header[0][0], 5)
    fig, ax = plt.subplots(q1, number_of_w_readed, figsize=(8, 8))
    for t in range(0, q1):
        offset = t*header[1][0]
        for w in range(0, number_of_w_readed):
            ax[t,w].plot(np.linspace(0, header[2][0], header[2][0]), waveform_f[offset], label="t: {:d} w{:d}".format(t,w))
#             ax[t,w].legend()
#             ax[t,w].set_yscale("log")
#             ax[t,w].set_ylim(top=4000)
            offset+=1

    plt.savefig(DEFAULT_PATH_ONLINE+'custom/pmt_f.png', bbox_inches='tight')
    plt.close()
    with open(DEFAULT_PATH_ONLINE+'custom/pmt_f.png', 'rb') as f:
        img_bytes = f.read()
    f.close()
    img_base64 = base64.b64encode(img_bytes).decode('utf-8')
    producer.send('midas-pmt-f'+TAG, value=img_base64)#.encode('utf-8'))
    producer.flush()

    q2 = min(header[0][1], 5)
    fig, ax = plt.subplots(q2, number_of_w_readed, figsize=(8, 8))
    for t in range(0, q2):
        offset = t*header[1][1]
        for w in range(0, number_of_w_readed):
            ax[t,w].plot(np.linspace(0, header[2][1], header[2][1]), waveform_s[offset], label="t: {:d} w{:d}".format(t,w))
#             ax[t,w].legend()
#             ax[t,w].set_yscale("log")
#             ax[t,w].ylim(top=3000)
            offset+=1
    
    plt.savefig(DEFAULT_PATH_ONLINE+'custom/pmt_s.png', bbox_inches='tight')
    plt.close()
    with open(DEFAULT_PATH_ONLINE+'custom/pmt_s.png', 'rb') as f:
        img_bytes = f.read()
    f.close()
    img_base64 = base64.b64encode(img_bytes).decode('utf-8')
    producer.send('midas-pmt-s'+TAG, value=img_base64)#.encode('utf-8'))
    producer.flush()
    if verbose:
        print("PMT Image produced")

    del fig, ax, img_bytes, img_base64, header, waveform_f, waveform_s
    return

def main(verbose=False):
    
    import numpy as np

    from datetime import datetime

    import time
    import base64
    import json
    import io

    import midas
    import midas.client

    import cygno as cy

    from kafka import KafkaProducer
    
    import requests
    import boto3
    from boto3sts import credentials as creds
    import urllib.parse
    import re 
    
    producer = KafkaProducer(
        bootstrap_servers=['localhost:9092'],
        value_serializer=lambda x: json.dumps(x).encode('utf-8')
    )    

    
    client = midas.client.MidasClient("rconsole")
    buffer_handle = client.open_event_buffer("SYSTEM",None,100000000)
    request_id = client.register_event_request(buffer_handle, sampling_type = 2) 
    
    odb_update   = 3 # probabilemnte da mettere in middleware 
    event_info   = {}
    end1 = time.time()
    fpath = os.path.dirname(os.path.realpath(sys.argv[0]))
    
    corrected  = client.odb_get("/Configurations/DRS4Correction") # odb.data['Configurations']['DRS4Correction']
    channels_offsets  = client.odb_get("/Configurations/DigitizerOffset") # odb.data['Configurations']['DigitizerOffset']
    if verbose:
        print (corrected, channels_offsets)

    
    while True:
        # 
        start1 = time.time()
        if (start1-end1) > odb_update:
            try:
                # update ODB
                odb = client.odb_get("/")
                # print(odb)
                odb_json = json.dumps(odb)
                producer.send('midas-odb-'+TAG, value=odb_json)
                producer.flush()
                end1 = time.time()
                if verbose:
                    print("DEBUG: ODB elapsed: {:.2f}, payload size {:.1f} kb".format(end1-start1,                                                           len(odb_json.encode('utf-8'))/1024))
                del odb, odb_json
            except Exception as e:
                print('ERROR >>> Midas ODB: {}'.format(e))
                continue


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

            ################
            ## loacal stuf
            ################
            image_update_time = client.odb_get("/middleware/image_update_time")
            imege_pmt_offset = image_update_time/2
            if verbose:
                print("DEBUG: banks", bank_names)
            if ('CAM0' in bank_names) and (int(time.time())%image_update_time==0): # CAM image
                try: 
                    image, _, _ = cy.daq_cam2array(event.banks['CAM0']) # matrice delle imagine
                    image_jpg(image, 95, 130, event_number, event_time, producer, verbose)
                except Exception as e:
                    print('ERROR >>> generate IMAGE exception occurred: {}'.format(e))
                    continue
            if ('DGH0' in bank_names) and (int(time.time()+imege_pmt_offset)%image_update_time==0): # PMTs wavform 
                try:
#                     header = cy.daq_dgz_full2header(event.banks['DGH0'], verbose=verbose)
#                     waveform_f, waveform_s = cy.daq_dgz_full2array(event.banks['DIG0'], header)
                    full_header= cy.daq_dgz_full2header(event.banks['DGH0'], verbose=verbose)
                    w_fast, w_slow = cy.daq_dgz_full2array(event.banks['DIG0'], full_header, verbose=verbose, 
                                                   corrected=corrected, ch_offset=channels_offsets)
                    
                    
                    pmt_jpg(full_header, w_fast, w_slow, producer, number_of_w_readed = 5, verbose=verbose)
                except Exception as e:
                    print('ERROR >>> generate PMTs exception occurred: {}'.format(e))
                    continue
                
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
