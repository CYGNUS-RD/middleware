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
import pre_reconstruction as pr
import time
import pandas as pd

import midas
import midas.client

import mysql.connector

import sys
import cygno as cy
import multiprocess

from json import dumps
from kafka import KafkaProducer

MAX_CPU_AVAILABLE   = multiprocess.cpu_count()
DAQ_ROOT            = os.environ['DAQ_ROOT']
DEFAULT_PATH_ONLINE = DAQ_ROOT+'/online/'

def image_jpg(image, vmin, vmax, event_number, event_time):
    
    im = plt.imshow(image, cmap='gray', vmin=vmin, vmax=vmax)
    plt.title ("Event: {:d} at {:s}".format(event_number, event_time))
    plt.savefig(DEFAULT_PATH_ONLINE+'custom/tmp.png')
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


def main(verbose=True):
    producer = KafkaProducer(
        bootstrap_servers=['localhost:9092'],
        value_serializer=lambda x: dumps(x).encode('utf-8')
    )
    client = midas.client.MidasClient("middleware")
    buffer_handle = client.open_event_buffer("SYSTEM",None,1000000000)
    request_id = client.register_event_request(buffer_handle, sampling_type = 2)#midas.GET_SOME)
    
    # init program variables
    t0 = time.time()
    vmin         = 95
    vmax         = 130
    connection   =-1
    max_try      = 3
    header_event = [
        'timestamp',
        'serial_number',
        'event_id']


    # global run useful varibles
    header_environment = client.odb_get("/Equipment/Environment/Settings/Names Input")
    header_environment = header_event + header_environment
    n_try=0
    while connection == -1 and n_try<=max_try:
        connection = init_sql()
        time.sleep(1)
        print (int(time.time()), "ERROR SQL connaction fail...", n_try)
        n_try+=1
    if connection == -1:
        exit(-1)
    while True:

        event = client.receive_event(buffer_handle, async_flag=True)
        state         = client.odb_get("/Runinfo/State")
        
        if event is not None:
            if event.header.is_midas_internal_event():
                if verbose:
                    print("Saw a special event")
                continue

            # global event useful variables
            bank_names    = ", ".join(b.name for b in event.banks.values())
            event_info    = [event.header.timestamp, event.header.serial_number, event.header.event_id]
            run_number    = client.odb_get("/Runinfo/Run number")
            event_number  = event.header.serial_number
            event_time    = datetime.fromtimestamp(event.header.timestamp).strftime('%Y-%m-%d %H:%M:%S')

            
            if 'CAM0' in bank_names: # CAM image
                image, _, _ = cy.daq_cam2array(event.banks['CAM0']) # matrice delle imagine
                image_update_time = client.odb_get("/middleware/image_update_time")
                if int(time.time())%image_update_time==0:
                    image_jpg(image, vmin, vmax, event_number, event_time)

            if 'INPT' in bank_names:                
                value = [event_info + list(event.banks['INPT'].data)]
                try:
                    producer.send('slow_control', value=value)
                except:
                    print (int(time.time()), "KAFKA ERROR...")

                de = pd.DataFrame(value, columns = header_environment)
                table_name_sc = "SlowControl"
                n_try=0
                while push_panda_table_sql(connection,table_name_sc, de) == -1 and n_try<=max_try:
                    time.sleep(1)
                    connection = init_sql()
                    print (int(time.time()), "ERROR SQL  push_panda_table_sql fail...", n_try, connection)
                n_try+=1
                if n_try==max_try:
                    exit(-1)
            if event_number%100==0:
                print ("midware alive", event_number)
                
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
