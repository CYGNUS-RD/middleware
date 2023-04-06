#!/usr/bin/env python3
#
# I. Abritta and G. Mazzitelli March 2022
# Middelware online recostruction 
# Modify by ... in date ...
#

from matplotlib import pyplot as plt
import numpy as np
import os
import stat
from datetime import datetime
# import pre_reconstruction as pr
import time
import pandas as pd
import base64
import io
import json
#import struct

import midas
import midas.client

import mysql.connector

import sys
import cygno as cy
import multiprocess
from multiprocessing import Pool, Process
from json import dumps
from kafka import KafkaProducer
# import cv2

MAX_CPU_AVAILABLE   = multiprocess.cpu_count()
DAQ_ROOT            = os.environ['DAQ_ROOT']
DEFAULT_PATH_ONLINE = DAQ_ROOT+'/online/'

def image_jpg(image, vmin, vmax, event_number, event_time, producer):
    
    im = plt.imshow(image, cmap='gray', vmin=vmin, vmax=vmax)
    plt.title ("Event: {:d} at {:s}".format(event_number, event_time))
    plt.savefig(DEFAULT_PATH_ONLINE+'custom/tmp.png')

    with open(DEFAULT_PATH_ONLINE+'custom/tmp.png', 'rb') as f:
        img_bytes = f.read()
    
    #image_to_kafka = base64.b64encode(cv2.imencode('.jpg', img)[1]).decode()
    img_base64 = base64.b64encode(img_bytes).decode('utf-8')
    producer.send('image-topic', value=img_base64.encode('utf-8'))
    
    return 

def push_panda_table_sql(connection, table_name, df):
    try:
        mycursor=connection.cursor()
        mycursor.execute("SHOW TABLES LIKE '"+table_name+"'")
        result = mycursor.fetchone()
        if not result:
            cols = "`,`".join([str(i) for i in df.columns.tolist()])
            db_to_crete = "CREATE TABLE `"+table_name+"` ("+' '.join(["`"+x+"` REAL," for x in df.columns.tolist()])[:-1]+")"
            print ("[Table {:s} created into SQL Server]".format(table_name))
            mycursor = connection.cursor()
            mycursor.execute(db_to_crete)

        cols = "`,`".join([str(i) for i in df.columns.tolist()])

        for i,row in df.iterrows():
            sql = "INSERT INTO `"+table_name+"` (`" +cols + "`) VALUES (" + "%s,"*(len(row)-1) + "%s)"
            mycursor.execute(sql, tuple(row.astype(str)))
            connection.commit()

        mycursor.close()
        return 0 
    except:
        return -1

def init_sql():
    import os
    import mysql.connector
    # init sql variabile and connector
    try:
        connection = mysql.connector.connect(
          host=os.environ['MYSQL_IP'],
          user=os.environ['MYSQL_USER'],
          password=os.environ['MYSQL_PASSWORD'],
          database=os.environ['MYSQL_DATABASE'],
          port=int(os.environ['MYSQL_PORT'])
        )
        return connection
    except:
        return -1
def send_data(producer, topic, data):
    producer.send('midas-event', value=data)
    producer.flush()
    return

def main(verbose=True):
    producer = KafkaProducer(
        bootstrap_servers=['localhost:9092'],
        value_serializer=lambda x: dumps(x).encode('utf-8')
    )
    producerb = KafkaProducer(
        bootstrap_servers=['localhost:9092'],
        #value_serializer=lambda m: json.dumps(m).encode('ascii'),
        #value_serializer=lambda v: dumps(v).encode('utf-8'),
        max_request_size= 31457280 #15728640,
        #max_block_ms=300000
    )
    
    
    client = midas.client.MidasClient("middleware")
    buffer_handle = client.open_event_buffer("SYSTEM",None,1000000000)
    request_id = client.register_event_request(buffer_handle, sampling_type = 2) #midas.GET_SOME)
    
    # init program variables #####
    t0 = time.time()
    vmin         = 95
    vmax         = 130
    connection   =-1
    max_try      = 3
    header_event = [
        'timestamp',
        'serial_number',
        'event_id']
    TAG         = os.environ['TAG']
    ###############################

    # global run useful varibles
    header_environment = client.odb_get("/Equipment/Environment/Settings/Names Input")
    header_environment = header_event + header_environment
    #
    n_try=0
    while connection == -1 and n_try<=max_try:
        connection = init_sql()
        time.sleep(1)
        n_try+=1
    if connection == -1:
        print (int(time.time()), "ERROR SQL connaction fail...")
        exit(-1)
    
    while True:
        start = time.time()
        event = client.receive_event(buffer_handle, async_flag=True)
#        state         = client.odb_get("/Runinfo/State")

        odb_json = dumps(client.odb_get("/"))
        producer.send('midas-odb', value=odb_json)
        end = time.time()
        print("ODB elapsed: {:.2f}, payload size {:.1f} kb".format(end-start, len(odb_json.encode('utf-8'))/1024))
        
        start = time.time()
        
        if event is not None:
            if event.header.is_midas_internal_event():
                if verbose:
                    print("Saw a special event")
                continue
                
            pyload = event.pack()
            binary_data = io.BytesIO()
            binary_data.write(pyload)
            binary_data.seek(0)
            encoded_data = binary_data.read()
#             p = Process(target=send_data, args=(producerb, 'midas-event', encoded_data))
#             p.start()
#             p.join()
#             with Pool() as pool:
#                 result = pool.map(send_data, producerb, 'midas-event', encoded_data)
            
            producerb.send('midas-event', value=(encoded_data))
            producerb.flush()
            
            
            end = time.time()
            print("EVENT elapsed: {:.2f}, payload size {:.1f} Mb timestamp {:} ".format(end-start, len(encoded_data)/1024/1024, event.header.timestamp))
            #print("EVENT elapsed: {:.2f}, payload size {:.1f} Mb encoded {:.1f} Mb".format(end-start, np.size(pyload)/1024/1024, np.size(encoded_data)/1024/1024))
            

            # global event useful variables
            bank_names    = ", ".join(b.name for b in event.banks.values())
            event_info    = [event.header.timestamp, event.header.serial_number, event.header.event_id]
            run_number    = client.odb_get("/Runinfo/Run number")
            event_number  = event.header.serial_number
            event_time    = datetime.fromtimestamp(event.header.timestamp).strftime('%Y-%m-%d %H:%M:%S')

            image_update_time = client.odb_get("/middleware/image_update_time")
            if ('CAM0' in bank_names) and (int(time.time())%image_update_time==0): # CAM image
                image, _, _ = cy.daq_cam2array(event.banks['CAM0']) # matrice delle imagine
                image_jpg(image, vmin, vmax, event_number, event_time, producerb)

#             if 'INPT' in bank_names:                
#                 value = [event_info + list(event.banks['INPT'].data)]
#                 try:
#                     producer.send('slow_control', value=value)
#                 except:
#                     print (int(time.time()), "KAFKA ERROR...")

#                 de = pd.DataFrame(value, columns = header_environment)
#                 table_name_sc = "SlowControl"
#                 n_try=0
#                 while push_panda_table_sql(connection,table_name_sc, de) == -1 and n_try<=max_try:
#                     time.sleep(1)
#                     connection = init_sql()
#                     print (int(time.time()), "ERROR SQL push_panda_table_sql fail...", n_try, connection)
#                 n_try+=1
#                 if n_try==max_try:
#                     exit(-1)
#             if event_number%100==0:
#                 print ("midware alive", event_number)
                
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
