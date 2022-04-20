#!/usr/bin/env python3
#
# I. Abritta and G. Mazzitelli March 2022
# Middelware online recostruction 
# Modify by ... in date ...
#
from matplotlib import pyplot as plt
import numpy as np
import os
from datetime import datetime
#import pre_reconstruction as pr
import time


import midas
import midas.client

DEFAULT_PED_VALUE = '99'
DEFAULT_VMIN_VALUE = '95'
DEFAULT_VMAX_VALUE = '120'

def main(grid, vmin=DEFAULT_VMIN_VALUE, vmax=DEFAULT_VMAX_VALUE, ped=DEFAULT_PED_VALUE, verbose=True):
    # Create our client
    client = midas.client.MidasClient("db_display")
    
    buffer_handle = client.open_event_buffer("SYSTEM",None,1000000000)

    request_id = client.register_event_request(buffer_handle)
    
    plt.figure(figsize = (10,10))
    y0=100 # grean frame limit
    print("Events display running..., Crtl-C to stop")
    print("Ped value, or file: "+ ped)
    if ped == DEFAULT_PED_VALUE:
        pad_varege_value = float(ped)
    vmin = int(vmin)
    vmax = int(vmax)
    while True:

        event = client.receive_event(buffer_handle, async_flag=False)
        if event.header.is_midas_internal_event():
            if verbose:
                print("Saw a special event")
            continue
        bank_names = ", ".join(b.name for b in event.banks.values())
        ev_number = event.header.serial_number
        if verbose:
            print("Event # %s of type ID %s contains banks %s" % (event.header.serial_number, event.header.event_id, bank_names))

            print("Received event with timestamp %s containing banks %s" % (event.header.timestamp, bank_names))
            print("%s, banks %s" % (datetime.utcfromtimestamp(event.header.timestamp).strftime('%Y-%m-%d %H:%M:%S'), bank_names))

        #if event is not None:
        if bank_names=='CAM0':

            shape = int(np.sqrt(event.banks['CAM0'].size_bytes*8/16))
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
            im = plt.imshow(image, cmap='gray', vmin=vmin, vmax=vmax)
        
            if grid:
                ax = plt.gca();

                majorx_ticks = np.arange(0, shape,  int(shape/11))
                majory_ticks = np.arange(0, shape,  int(shape/11))
                # Major ticks
                ax.set_xticks(majorx_ticks)
                ax.set_yticks(majory_ticks)

                # Labels for major ticks
                ax.set_xticklabels(majorx_ticks)
                ax.set_yticklabels(majory_ticks)

                ax.grid(color='r', linestyle='--', linewidth=1)

                ax.hlines(y0, 0, shape-1, colors='g')
                ax.hlines(shape-y0, 0, shape-1, colors='g')
                ax.vlines(y0, 0, shape-1, colors='g')
                ax.vlines(shape-y0, 0,shape-1, colors='g')

            plt.pause(0.05)
            
        client.communicate(10)

    client.deregister_event_request(buffer_handle, request_id)

    client.disconnect()
    
    
if __name__ == "__main__":
    from optparse import OptionParser
    parser = OptionParser(usage='usage: %prog\t ')
    parser.add_option('-g','--grid', dest='grid', action="store_true", default=False, help='grid;');
    parser.add_option('-n','--vmin', dest='vmin', action="store", type="string", default=DEFAULT_VMIN_VALUE, help='vmin, dafaul = ' + DEFAULT_VMIN_VALUE);
    parser.add_option('-m','--vmax', dest='vmax', action="store", type="string", default=DEFAULT_VMAX_VALUE, help='vman, dafaul = ' + DEFAULT_VMAX_VALUE);
    parser.add_option('-p','--ped', dest='ped', action="store", type="string", default=DEFAULT_PED_VALUE, help='pedestal file path, if none 99 value assumed for all points;');
    parser.add_option('-v','--verbose', dest='verbose', action="store_true", default=False, help='verbose output;');
    (options, args) = parser.parse_args()
    main(grid=options.grid, vmin=options.vmin, vmax=options.vmax,  ped=options.ped, verbose=options.verbose)

