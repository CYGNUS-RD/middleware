#!/usr/bin/env python3
from kafka import KafkaConsumer
# from json import loads
import time
import numpy as np
import io
from json import loads, dump
from midas import event
import midas
import pandas as pd
import mysql.connector
from datetime import datetime

import cygno as cy

import os
import sys
TAG='LNGS'

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

def main(verbose=False):
    vmin         = 95
    vmax         = 130
    connection   =-1
    max_try      = 3
    header_event = [
        'timestamp',
        'serial_number',
        'event_id']
    consumer = KafkaConsumer(
        'midas-event-file-'+TAG,
        bootstrap_servers=['localhost:9092'],
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        group_id='online-event',
        value_deserializer=lambda x: loads(x.decode('utf-8'))
    )
    event = midas.event.Event()
    consumer.poll()
    consumer.seek_to_end()
    for msg in consumer:
        start = time.time()
        event_data = msg.value
        event_info_json = loads(event_data)
        print(event_info_json)
        payload_name =  "/tmp/{}_{}_{}.dat".format(TAG, event_info_json["timestamp"],
                                                   event_info_json["serial_number"])
        end = time.time()
        print("Elapsed: {:.1f} s".format(end-start))
        try:
            start = time.time()
            with open(payload_name, "rb") as f:
                    payload = f.read()
            cy.cmd.rm_file(payload_name)
            event.unpack(payload, use_numpy=False)
            # print("received {:.1f} Mb message: {:}".format( len(msg.value)/1024/1024, msg.value[0:20]))
            bank_names = ", ".join(b.name for b in event.banks.values())
            # print(type(binary_data), type(pyload), (event.header.timestamp))
            bank_names    = ", ".join(b.name for b in event.banks.values())
            event_info    = [event.header.timestamp, event.header.serial_number, event.header.event_id]
            event_number  = event.header.serial_number
            event_time    = datetime.fromtimestamp(event.header.timestamp).strftime('%Y-%m-%d %H:%M:%S')
            print (event_info, bank_names)
            if ('CAM0' in bank_names):
                image, _, _ = cy.daq_cam2array(event.banks['CAM0']) # matrice delle imagine
                image_jpg(image, vmin, vmax, event_number, event_time)

            end = time.time()
            print("Elapsed: {:.1f} s".format(end-start))
        except:
            print ("ERROR")
        
        
        
if __name__ == "__main__":
    from optparse import OptionParser
    parser = OptionParser(usage='usage: %prog\t ')
    parser.add_option('-v','--verbose', dest='verbose', action="store_true", default=False, help='verbose output;');
    (options, args) = parser.parse_args()
    main(verbose=options.verbose)
