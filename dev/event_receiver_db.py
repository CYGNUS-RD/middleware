"""
A simple client that registers to receive events from midas.
"""

from matplotlib import pyplot as plt
import numpy as np
import os
from datetime import datetime
import pre_reconstruction as pr
import time


import midas
import midas.client

import mysql.connector


def makeped(ped_array):
    #print(np.shape(ped_array))
    
    pedarr_fr = np.mean(ped_array, axis=0)
    sigarr_fr = np.std(ped_array, axis=0)
    #print(pedarr_fr[1:100,1])
    return np.array(pedarr_fr), np.array(sigarr_fr)

def run_reco(image,runnumber,ev_number,pedarr_fr, sigarr_fr):
  
   
    #print ("New image arrived")
    #print ("Analyzing Run%05d Image %04d"% (runnumber,ev_number))
    ## Load image
    arr = image
    ## Include some reconstruction code here
    #
    t1 = time.time()
    variables = pr.pre_reconstruction(arr,runnumber,ev_number,pedarr_fr,sigarr_fr,printtime=True)
    t2 = time.time()

    df = pr.create_pandas(variables)
    return df

def push_panda_table_sql(connection, table_name, df):
    #mycursor = connection.cursor()
    
    mycursor=connection.cursor()
    
    mycursor.execute("SHOW TABLES LIKE '"+table_name+"'")
    result = mycursor.fetchone()
    if not result:
        cols = "`,`".join([str(i) for i in df.columns.tolist()])
        db_to_crete = "CREATE TABLE `"+table_name+"` ("+' '.join(["`"+x+"` REAL," for x in df.columns.tolist()])[:-1]+")"

        #print (db_to_crete)
        #
        # scommentare per eseguire
        #
        mycursor = connection.cursor()
        mycursor.execute(db_to_crete)

    cols = "`,`".join([str(i) for i in df.columns.tolist()])
    #print(cols)
    # Insert DataFrame recrds one by one.
    for i,row in df.iterrows():
        sql = "INSERT INTO `"+table_name+"` (`" +cols + "`) VALUES (" + "%s,"*(len(row)-1) + "%s)"
        #print (sql, tuple(row.astype(str)))
        mycursor.execute(sql, tuple(row.astype(str)))

        # the connection is not autocommitted by default, so we must commit to save our changes
        connection.commit()
    
    
    
#     mycursor.execute("SHOW TABLES LIKE '"+table_name+"'")
#     result = mycursor.fetchone()
#     if result:
#         # there is a table named "tableName"
#         print("bravo")
#     else:
#         print("pippa")
#     return

connection = mysql.connector.connect(
  host="131.154.96.215",
  user="cygno_producer",
  password="e3b46beda9650197978b7b7e80464f73",
  database="cygno_db",
  port=6033
)

mycursor = connection.cursor()

header_environment = [
    'P0IIn0',
    'P0IIn1',
    'P0IIn2',
    'P0IIn3',
    'P0IIn4',
    'P0IIn5',
    'P0IIn6',
    'P0IIn7',
    'P0Calib',
    'P1UIn0',
    'P1UIn1',
    'P1UIn2',
    'P1UIn3',
    'P1UIn4',
    'P1UIn5',
    'P1UIn6',
    'P1UIn7',
    'P1Calib',
    'P3IIn0',
    'P3IIn1',
    'P3IIn2',
    'P3IIn3',
    'P3IIn4',
    'P3IIn5',
    'P3IIn6',
    'P3IIn7',
    'P3Calib']

header_event = [
    'timestamp',
    'serial_number',
    'event_id']

header_event.extend(header_environment)

if __name__ == "__main__":
    # Create our client
    client = midas.client.MidasClient("db_producer")
    
    # Define which buffer we want to listen for events on (SYSTEM is the 
    # main midas buffer).
    buffer_handle = client.open_event_buffer("SYSTEM",None,1000000000)
    
    # Request events from this buffer that match certain criteria. In this
    # case we will only be told about events with an "event ID" of 14.
    # request_id = client.register_event_request(buffer_handle, event_id = 1)
    request_id = client.register_event_request(buffer_handle)
    
    ped_array = []
    ped_size = 1000
    ped_id = 0
    ped_flag = True
    
    while True:
        # If there's an event ready, `event` will contain a `midas.event.Event`
        # object. If not, it will be None. If you want to block waiting for an
        # event to arrive, you could set async_flag to False.
        # event = client.receive_event(buffer_handle, async_flag=True)
        event = client.receive_event(buffer_handle, async_flag=False)
        if event.header.is_midas_internal_event():
            print("Saw a special event")
            continue
        bank_names = ", ".join(b.name for b in event.banks.values())
        print("Event # %s of type ID %s contains banks %s" % (event.header.serial_number, event.header.event_id, bank_names))
        print("Received event with timestamp %s containing banks %s" % (event.header.timestamp, bank_names))
        print("%s, banks %s" % (datetime.utcfromtimestamp(event.header.timestamp).strftime('%Y-%m-%d %H:%M:%S'), bank_names))
        event_info = [event.header.timestamp, event.header.serial_number, event.header.event_id]

        #if event is not None:
        if bank_names=='CAM0':

            shape = int(event.banks['CAM0'].size_bytes/2**12)
            image = np.reshape(event.banks['CAM0'].data, (shape, shape))
            
            image = np.reshape(event.banks['CAM0'].data, (shape, shape))
            if ped_flag:
                
                if ped_id >= ped_size:
                    pedarr_fr, sigarr_fr = makeped(ped_array)
                    ped_flag = False
                else:
                    ped_array.append(image)
                    ped_id+=1
            else:
                #print(image[1:100,1])
                runnumber = client.odb_get("/Runinfo/Run number")
                table_name = "Run{:05d}".format(runnumber)
                df = run_reco(image,runnumber,event.header.serial_number,pedarr_fr, sigarr_fr)
                push_panda_table_sql(connection,table_name, df)
                #df.to_sql("Run10000", con=connection, if_exists='append', index_label='id')
            
        if bank_names=='DGH0':
            Waveform=[]

            ndgtz = event.banks['DGH0'].data[2]
            NCHDGTZ =  event.banks['DGH0'].data[3]
            NumEvents = event.banks['DGH0'].data[4]

            for i in range(ndgtz):
                Waveform.append(event.banks['DIG0'].data[i])
            x=np.arange(ndgtz)
            
        if bank_names=='INPT':
            print(datetime.utcfromtimestamp(event.header.timestamp).strftime('%Y-%m-%d %H:%M:%S'), 
                  "event: "+str(event.header.serial_number))
            print("  >>>  Entry in bank %s is %s" % (bank_names, event.banks['INPT'].data))
            value = event_info + list(event.banks['INPT'].data)
            sql = "INSERT INTO `environment` ("+" ".join(["`"+hed+"`," for hed in header_event])[:-1]+") VALUES ("+",".join([str(x) for x in value])+" )"
            # print (sql)
            mycursor = connection.cursor()
            mycursor.execute(sql)
            connection.commit()
            print(mycursor.rowcount, "Record inserted successfully into Laptop table")
            


       # Talk to midas so it knows we're alive, or can kill us if the user
        # pressed the "stop program" button.
        client.communicate(10)
        
    # You don't have to cancel the event request manually (it will be done
    # automatically when the program exits), but for completeness we're just
    # showing that such a function exists.
    client.deregister_event_request(buffer_handle, request_id)
    # plt.show()
    
    # Disconnect from midas before we exit.
    mycursor.close()
    client.disconnect()
    
