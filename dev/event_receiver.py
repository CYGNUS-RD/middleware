"""
A simple client that registers to receive events from midas.
"""

from matplotlib import pyplot as plt
import numpy as np
import os


import midas
import midas.client

if __name__ == "__main__":
    # Create our client
    client = midas.client.MidasClient("pytest")
    
    # Define which buffer we want to listen for events on (SYSTEM is the 
    # main midas buffer).
    buffer_handle = client.open_event_buffer("SYSTEM",None,1000000000)
    
    # Request events from this buffer that match certain criteria. In this
    # case we will only be told about events with an "event ID" of 14.
    request_id = client.register_event_request(buffer_handle, event_id = 1)
    
    while True:
        # If there's an event ready, `event` will contain a `midas.event.Event`
        # object. If not, it will be None. If you want to block waiting for an
        # event to arrive, you could set async_flag to False.
        event = client.receive_event(buffer_handle, async_flag=True)

        if event is not None:

            Waveform=[]
        
            ndgtz = event.banks['DGH0'].data[2]
            NCHDGTZ =  event.banks['DGH0'].data[3]
            NumEvents = event.banks['DGH0'].data[4]

            for i in range(ndgtz):
                Waveform.append(event.banks['DIG0'].data[i])
            x=np.arange(ndgtz)

            plt.clf()
            plt.plot(x,Waveform)
            plt.pause(0.05)

            print(event.banks['CAM0'].data[1000])
            # Print some information to screen about this event.
            #bank_names = ", ".join(b.name for b in event.banks)
            #print("Received event with timestamp %s containing banks %s" % (event.header.timestamp, bank_names))
            
        # Talk to midas so it knows we're alive, or can kill us if the user
        # pressed the "stop program" button.
        client.communicate(10)
        
    # You don't have to cancel the event request manually (it will be done
    # automatically when the program exits), but for completeness we're just
    # showing that such a function exists.
    client.deregister_event_request(buffer_handle, request_id)
    plt.show()
    
    # Disconnect from midas before we exit.
    client.disconnect()
    
