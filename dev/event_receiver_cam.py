"""
A simple client that registers to receive events from midas.
"""

from matplotlib import pyplot as plt
import numpy as np
import os
from datetime import datetime
#import pre_reconstruction as pr
import time


import midas
import midas.client


if __name__ == "__main__":
    # Create our client
    client = midas.client.MidasClient("db_display")
    
    # Define which buffer we want to listen for events on (SYSTEM is the 
    # main midas buffer).
    buffer_handle = client.open_event_buffer("SYSTEM",None,1000000000)
    
    # Request events from this buffer that match certain criteria. In this
    # case we will only be told about events with an "event ID" of 14.
    # request_id = client.register_event_request(buffer_handle, event_id = 1)
    request_id = client.register_event_request(buffer_handle)
    
    plt.figure(figsize = (10,10))
    
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
        ev_number = event.header.serial_number
        print("Received event with timestamp %s containing banks %s" % (event.header.timestamp, bank_names))
        print("%s, banks %s" % (datetime.utcfromtimestamp(event.header.timestamp).strftime('%Y-%m-%d %H:%M:%S'), bank_names))

        #if event is not None:
        if bank_names=='CAM0':

            shape = int(event.banks['CAM0'].size_bytes/2**12)
            image = np.reshape(event.banks['CAM0'].data, (shape, shape))
#             if ped_flag:
                
#                 if ped_id >= ped_size:
#                     pedarr_fr, sigarr_fr = makeped(ped_array)
#                     ped_flag = False
#                 else:
#                     ped_array.append(image)
#                     ped_id+=1
#             else:
#                 print(image[1:100,1])
#                 runnumber = client.odb_get("/Runinfo/Run number")
#                 run_reco(image,runnumber,ev_number,pedarr_fr, sigarr_fr)

            plt.clf()
            # plt.imshow(image)
                # plt.imshow(image, cmap='YlGnBu')

            plt.imshow(image, cmap='gray', vmin=95, vmax=105)

            #majorx_ticks = np.arange(0, np.size(image),  int(np.size(image)/11))
            #majory_ticks = np.arange(0, np.size(image),  int(np.size(image)/11))
                #y0=100
    #            plt.hlines(y0, 0, np.size(image)-1, colors='g')
    #             plt.hlines(np.size(image)-y0, 0, np.size(image)-1, colors='g')
    #             plt.vlines(y0, 0, np.size(image)-1, colors='g')
    #             plt.vlines(np.size(image)-y0, 0, np.size(image)-1, colors='g')

    #             plt.grid(color='r', linestyle='--', linewidth=1)
    #             plt.xticks(majorx_ticks)
    #             plt.yticks(majory_ticks)
            plt.pause(0.05)
            
            
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


       # Talk to midas so it knows we're alive, or can kill us if the user
        # pressed the "stop program" button.
        client.communicate(10)
        
    # You don't have to cancel the event request manually (it will be done
    # automatically when the program exits), but for completeness we're just
    # showing that such a function exists.
    client.deregister_event_request(buffer_handle, request_id)
    # plt.show()
    
    # Disconnect from midas before we exit.
    client.disconnect()
    
