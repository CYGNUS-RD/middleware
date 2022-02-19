"""
A simple client that registers to receive events from midas.
"""

from matplotlib import pyplot as plt
import numpy as np
import os
from datetime import datetime


import midas
import midas.client

import mysql.connector

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
    
