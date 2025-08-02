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
import time
import pandas as pd

import midas
import midas.client

import mysql.connector

import sys
import cygno as cy
import multiprocess


MAX_CPU_AVAILABLE   = multiprocess.cpu_count()
DAQ_ROOT            = os.environ['DAQ_ROOT']
DEFAULT_PATH_ONLINE = DAQ_ROOT+'/online/'

def image_jpg(image, vmin, vmax, event_number, event_time):
    
    im = plt.imshow(image, cmap='gray', vmin=vmin, vmax=vmax)
    plt.title ("Event: {:d} at {:s}".format(event_number, event_time))
    plt.savefig(DEFAULT_PATH_ONLINE+'custom/tmp.png')
    return 

def push_panda_table_sql(connection, table_name, df, verbose=False):
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
            if verbose: print(sql)
            mycursor.execute(sql, tuple(row.astype(str)))
            connection.commit()

        mycursor.close()
        return 0 
    except:
        return -1
    
def daq_sql_connection_local(verbose=False):
    import mysql.connector
    import os
    try:
        connection = mysql.connector.connect(
          host='localhost',
          user=os.environ['MYSQL_USER'],
          password=os.environ['MYSQL_PASSWORD'],
          database=os.environ['MYSQL_DATABASE'],
          port=3306
        )
        if verbose: print(connection)
        return connection
    except:
        return -1

    
def init_sql(verbose):
    import os
    import mysql.connector
    # init sql variabile and connector
    host=os.environ['MYSQL_IP'],
    user=os.environ['MYSQL_USER'],
    password=os.environ['MYSQL_PASSWORD'],
    database=os.environ['MYSQL_DATABASE'],
    port=int(os.environ['MYSQL_PORT'])
    if verbose: print(host, user, password, database, port)

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


def main(verbose):

    client = midas.client.MidasClient("middleware")
    buffer_handle = client.open_event_buffer("SYSTEM",None,1000000000)
    request_id = client.register_event_request(buffer_handle, sampling_type = 2)#midas.GET_SOME)
    
    # init program variables
    t0 = time.time()
    connection   =-1
    max_try      = 3
    header_event = [
        'timestamp',
        'serial_number',
        'event_id']


    # global run useful varibles
    header_environment = client.odb_get("/Equipment/Environment/Settings/Names Input")
    header_environment = header_event + header_environment
    table_name_sc = "SCS"
    
    n_try=1
    while connection == -1 and n_try<=max_try:
        connection =  daq_sql_connection_local(verbose)
        # connection = init_sql(verbose)
        time.sleep(1)
        n_try+=1
    if connection == -1:
        print (int(time.time()), "ERROR SQL connaction fail...", n_try)
        sys.exit(1)
        
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

            
            if 'INPT' in bank_names:                
                value = [event_info + list(event.banks['INPT'].data)]
                if verbose: print(len(header_environment), len(value), value)
                if event.header.event_id==5:
                    de = pd.DataFrame(value, columns = header_environment)
                    # if verbose: print(de)
                    de.replace(np.nan, -99, inplace=True)                
                    if verbose: print('sendig data', de)
                    n_try=0
                    while push_panda_table_sql(connection,table_name_sc, de, verbose) == -1 and n_try<max_try:
                        time.sleep(1)
                        # connection = daq_sql_connection_local(verbose)
                        n_try+=1
                        print(n_try)
                    if n_try==max_try:
                       print (int(time.time()), "ERROR SQL  push_panda_table_sql fail...", n_try, connection)
                       sys.exit(1)
            if event_number%100==0:
                print ("midware alive", event_number)
                
        client.communicate(10)
        time.sleep(0.1)
        
    client.deregister_event_request(buffer_handle, request_id)

    client.disconnect()
    sys.exit(0)
        
if __name__ == "__main__":
    from optparse import OptionParser
    parser = OptionParser(usage='usage: %prog\t ')
    parser.add_option('-v','--verbose', dest='verbose', action="store_true", default=False, help='verbose output;');
    (options, args) = parser.parse_args()
    main(verbose=options.verbose)
