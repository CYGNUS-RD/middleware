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

# def image_jpg(image, vmin, vmax, event_number, event_time):
#     from matplotlib import pyplot as plt
#     im = plt.imshow(image, cmap='gray', vmin=vmin, vmax=vmax)
#     plt.title ("Event: {:d} at {:s}".format(event_number, event_time))
#     plt.savefig(DEFAULT_PATH_ONLINE+'custom/tmp.png')
#     plt.close()
#     del image, im
#     return 

def image_jpg(image, vmin, vmax, event_number, event_time, producer, verbose=False):
    from matplotlib import pyplot as plt
    import numpy as np
    import base64
    
    im = plt.imshow(image, cmap='gray', vmin=vmin, vmax=vmax)
    plt.title ("Event: {:d} at {:s}".format(event_number, event_time))
    plt.savefig(DEFAULT_PATH_ONLINE+'custom/tmp.png')#, bbox_inches='tight'
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

def pmt_jpg(header, waveform_f, producer, number_of_w_readed = 5, verbose=False):
    from matplotlib import pyplot as plt
    import numpy as np
    import base64
    
    fig, ax = plt.subplots(header[0][0], number_of_w_readed, figsize=(10, header[1][0]))
    for t in range(0, header[0][0]):
        offset = t*header[1][0]
        for w in range(0, number_of_w_readed):
            ax[t,w].plot(np.linspace(0, header[2][0], header[2][0]), waveform_f[offset], label="t: {:d} w{:d}".format(t,w))
            ax[t,w].legend()
            offset+=1
    plt.savefig(DEFAULT_PATH_ONLINE+'custom/pmt.png')
    plt.close()
    with open(DEFAULT_PATH_ONLINE+'custom/pmt.png', 'rb') as f:
        img_bytes = f.read()
    f.close()
    img_base64 = base64.b64encode(img_bytes).decode('utf-8')
    producer.send('midas-pmt-'+TAG, value=img_base64)#.encode('utf-8'))
    producer.flush()
    if verbose:
        print("CAMEARA Image produced")

    del fig, ax, img_bytes, img_base64, header, waveform_f
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
    session = creds.assumed_session("infncloud-wlcg", endpoint="https://minio.cloud.infn.it/", verify=True)
    s3 = session.client('s3', endpoint_url="https://minio.cloud.infn.it/", config=boto3.session.Config(signature_version='s3v4'),
                                                verify=True)
    
    client = midas.client.MidasClient("middleware")
    buffer_handle = client.open_event_buffer("SYSTEM",None,1000000000)
    request_id = client.register_event_request(buffer_handle, sampling_type = 2) 
    
    odb_update   = 3 # probabilemnte da mettere in middleware 
    event_info   = {}
    end1 = time.time()
    fpath = os.path.dirname(os.path.realpath(sys.argv[0]))
    
    
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
            event_info["timestamp"]             = event.header.timestamp
            event_info["serial_number"]         = event.header.serial_number
            event_info["event_id"]              = event.header.event_id
            event_info["trigger_mask"]          = event.header.trigger_mask
            event_info["event_data_size_bytes"] = event.header.event_data_size_bytes
            event_info["run_number"]            = run_number
            event_info_json                     = json.dumps(event_info)
            # #################
            # upload EVENT on S3
            # #################
            payload = event.pack()
            payload_name =  "{}_{}_{}.dat".format(TAG, event.header.timestamp, event_number)
#
# esempio con presigned url, il piu' lento
#             try:
#                 url_out = s3.generate_presigned_post('cygno-data','EVENTS/'+payload_name, ExpiresIn=3600)
#             except:
#                 print("presigned post error")
#                 continue

#             files = {'file': (payload_name, payload)}
#             try:
#                 http_response = requests.post(url_out['url'], data=url_out['fields'], files=files, timeout=5)
#             except requests.exceptions.RequestException as e:
#                 print(e)
#                 continue
# esempio con scrittura e invio file un po' piu' veloce
#            try:
#                 with open('/tmp/'+payload_name, "wb") as f:
#                     f.write(payload)
#                 s3.upload_file('/tmp/'+payload_name, 'cygno-data', 'EVENTS/'+payload_name)
# 
            try:
                binary_data = io.BytesIO()
                binary_data.write(payload)
                binary_data.seek(0)
                s3.put_object(Body=binary_data.read(), Bucket='cygno-data', Key='EVENTS/'+payload_name)
            except Exception as e:
                print('ERROR >>> S3 put object exception occurred: {}'.format(e))
                continue
                
            finally:
                end2 = time.time()
                producer.send('midas-event-file-'+TAG, value=event_info_json)
                #producer.flush()
                if verbose: 
                    print("DEBUG: elapsed: {:.2f}, payload size {:.1f} Mb, timestamp {:}, Run Number {:}, Event Number {:}, Event ID {:} ".format(end2-start2, np.size(payload)/1024/1024, 
                                                        event.header.timestamp, run_number, event_number, 
                                                        event.header.event_id))

            ################
            ## loacal stuf
            ################
            image_update_time = client.odb_get("/middleware/image_update_time")
            imege_pmt_offset = image_update_time/2
            if ('CAM0' in bank_names) and (int(time.time())%image_update_time==0): # CAM image
                try: 
                    image, _, _ = cy.daq_cam2array(event.banks['CAM0']) # matrice delle imagine
                    image_jpg(image, 95, 130, event_number, event_time, producer, verbose)
                except Exception as e:
                    print('ERROR >>> generate IMAGE exception occurred: {}'.format(e))
                    continue
#             if ('DGH0' in bank_names) and (int(time.time()+imege_pmt_offset)%image_update_time==0): # PMTs wavform 
#                 try:
#                     header = cy.daq_dgz_full2header(bank, verbose=False)
#                     waveform_f, waveform_s = cy.daq_dgz_full2array(event.banks['DIG0'], header)
#                     pmt_jpg(header, waveform_f, producer, number_of_w_readed = 5, verbose=verbose)
#                 except Exception as e:
#                     print('ERROR >>> generate PMTs exception occurred: {}'.format(e))
#                     continue
                
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
