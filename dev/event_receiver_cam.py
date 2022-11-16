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
import sys

DEFAULT_PED_VALUE = '99'
DEFAULT_VMIN_VALUE = '-5'
DEFAULT_VMAX_VALUE = '30'
DEFAULT_FRAME_VALUE= '100' # grean frame limit

def image_jpg(bank, vmin, vmax, grid, event_number, event_time, pedarr_fr, y0=DEFAULT_FRAME_VALUE):

    shape = int(np.sqrt(bank.size_bytes*8/16))
    image = np.reshape(bank.data, (shape, shape))

    im = plt.imshow(image-pedarr_fr, cmap='gray', vmin=vmin, vmax=vmax)
    plt.title ("Event: {:d} at {:s}".format(event_number, event_time))
    plt.savefig('/home/standard/daq/online/custom/tmp.png')
    return 

def image_plot(bank, vmin, vmax, grid, event_number, event_time, pedarr_fr, y0=DEFAULT_FRAME_VALUE):

    shape = int(np.sqrt(bank.size_bytes*8/16))   
    image = np.reshape(bank.data, (shape, shape))
    
    print(np.mean(image), np.std(image))
    
    plt.clf()
    im = plt.imshow(image-pedarr_fr, cmap='gray', vmin=vmin, vmax=vmax)


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
    plt.title ("Event: {:d} at {:s}".format(event_number, event_time))
    #plt.pause(0.05)

def loadped(pedarr_fr, exposure_time):
    exposure_time_old = exposure_time
    if not len(pedarr_fr):
        try:
            print("Loading ped file")
            pedarr_fr = np.load("pedarr_%.1f.npy" % exposure_time)
        except:
            print("Using fixed ped = 99")
            #pedarr_fr = 99*np.ones((2304,2304),dtype=int)
            pedarr_fr = 100*np.ones((2304,2304),dtype=int)
    return pedarr_fr, exposure_time_old
    
    
def main(grid=False, vmin=DEFAULT_VMIN_VALUE, vmax=DEFAULT_VMAX_VALUE, ped=DEFAULT_PED_VALUE, 
         y0=DEFAULT_FRAME_VALUE, verbose=True):
    
    pedarr_fr    = []
    # Create our client
    client = midas.client.MidasClient("db_display")
    
    buffer_handle = client.open_event_buffer("SYSTEM",None,1000000000)

    request_id = client.register_event_request(buffer_handle)
    
    plt.ion()
    fig = plt.figure(figsize = (10,10))

    print("Events display running..., Crtl-C to stop")
    print("Ped value, or file: "+ ped)
    if ped == DEFAULT_PED_VALUE:
        pad_varege_value = float(ped)
        
    print("Image range vmin: {:s}, vmax: {:s}".format(vmin, vmax))
    vmin = int(vmin)
    vmax = int(vmax)
    y0 = int(y0)
    t0 = time.time()
    while True:
        try:
            event = client.receive_event(buffer_handle, async_flag=False)
            if event.header.is_midas_internal_event():
                if verbose:
                    print("Saw a special event")
                continue
            bank_names = ", ".join(b.name for b in event.banks.values())
            event_number = event.header.serial_number
            event_time = datetime.fromtimestamp(event.header.timestamp).strftime('%Y-%m-%d %H:%M:%S')
            if verbose:
                print("Event # %s of type ID %s contains banks %s" % (event_number, event.header.event_id, bank_names))

                print("Received event with timestamp %s containing banks %s" % (event.header.timestamp, bank_names))
                print("%s, banks %s" % (event_time, bank_names))

            #if event is not None:
            if bank_names=='CAM0':
                t1 = time.time()
                exposure_time = client.odb_get("/Configurations/Exposure")
                
                pedarr_fr, exposure_time_old = loadped(pedarr_fr, exposure_time)
                if exposure_time != exposure_time_old:
                    pedarr_fr = []
                    pedarr_fr, exposure_time_old = loadped(pedarr_fr, exposure_time)
                
                image_plot(event.banks['CAM0'], vmin, vmax, grid, event_number, event_time, pedarr_fr, y0)
                fig.canvas.flush_events()
                time.sleep(0.05)
                #if (t1-t0) > 30:
                #    image_jpg(event.banks['CAM0'], vmin, vmax, grid, event_number, event_time, pedarr_fr, y0)
                #    t0 = time.time()
                
                
                

            client.communicate(10)
        except KeyboardInterrupt:
            client.deregister_event_request(buffer_handle, request_id)
            client.disconnect()
            print ("\nBye, bye...")
            sys.exit()

    
    
if __name__ == "__main__":
    from optparse import OptionParser
    parser = OptionParser(usage='usage: %prog\t ')
    parser.add_option('-g','--grid', dest='grid', action="store_true", default=False, help='grid;');
    parser.add_option('-n','--vmin', dest='vmin', action="store", type="string", default=DEFAULT_VMIN_VALUE, help='vmin, dafaul = ' + DEFAULT_VMIN_VALUE);
    parser.add_option('-m','--vmax', dest='vmax', action="store", type="string", default=DEFAULT_VMAX_VALUE, help='vman, dafaul = ' + DEFAULT_VMAX_VALUE);
    parser.add_option('-p','--ped', dest='ped', action="store", type="string", default=DEFAULT_PED_VALUE, help='pedestal file path, if none 99 value assumed for all points;');
    parser.add_option('-y','--y0', dest='y0', action="store", type="string", default=DEFAULT_FRAME_VALUE, help='green frame (pixel) = ' + DEFAULT_FRAME_VALUE);
    parser.add_option('-v','--verbose', dest='verbose', action="store_true", default=False, help='verbose output;');
    (options, args) = parser.parse_args()
    main(grid=options.grid, vmin=options.vmin, vmax=options.vmax,  ped=options.ped, y0=options.y0, verbose=options.verbose)

