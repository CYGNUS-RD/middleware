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

import cygno as cy

import midas
import midas.client
import sys

DEFAULT_PED_VALUE   = '99'
DEFAULT_VMIN_VALUE  = '95'
DEFAULT_VMAX_VALUE  = '120'
DEFAULT_FRAME_VALUE = '100' # grean frame limit
DEFAULT_PMT_VALUE   = '5'

divisions = np.array([12,12])

def find_stdArray(img_arr, divisions, overlap = 30):
    
    n_evs = np.shape(img_arr)[0]
    size = np.shape(img_arr)[1]
    div_size = size/divisions
    
    std_arr = np.zeros([n_evs, divisions[0]*divisions[1]], dtype = float)
    
    for ev in range(n_evs):
        img = img_arr[ev]

        x, y = np.meshgrid(np.arange(divisions[0]), np.arange(divisions[1]))

        #print("Image: %.3f \u00B1 %.3f" %(np.mean(img.flatten()), np.std(img.flatten())))
        for k in range(divisions[0]*divisions[1]):
            xx = x.flatten()[k]
            yy = y.flatten()[k]

            x_begin = int(xx*div_size[0])
            x_end = int((xx+1)*div_size[0])

            y_begin = int(yy*div_size[1])
            y_end = int((yy+1)*div_size[1])

            x_begin = x_begin - (overlap if x_begin != 0 else 0)
            x_end = x_end + (overlap if x_end != 2304 else 0)

            y_begin = y_begin - (overlap if y_begin != 0 else 0)
            y_end = y_end + (overlap if y_end != 2304 else 0)


            img_div = img[x_begin:x_end, y_begin:y_end]
            std_arr[ev,k] = np.std(img_div)

    return std_arr


def trigger(std_arr, threshold):
    
    trigger_arr = std_arr > threshold
    return np.where(trigger_arr)[0]

def plot_image(ax, bank, vmin, vmax, grid, event_number, event_time, trigger_position, divisions, y0=DEFAULT_FRAME_VALUE, overlap = 30):

    shape = int(np.sqrt(bank.size_bytes*8/16))
    image = np.reshape(bank.data, (shape, shape))
    
    
    ax[0].imshow(image, cmap='gray', vmin=vmin, vmax=vmax)
    plt.title ("Event: {:d} at {:s}".format(event_number, event_time))
    if grid:
        ax[0] = plt.gca();

        majorx_ticks = np.arange(0, shape,  int(shape/11))
        majory_ticks = np.arange(0, shape,  int(shape/11))
        # Major ticks
        ax[0].set_xticks(majorx_ticks)
        ax[0].set_yticks(majory_ticks)

        # Labels for major ticks
        ax[0].set_xticklabels(majorx_ticks)
        ax[0].set_yticklabels(majory_ticks)

        ax[0].grid(color='r', linestyle='--', linewidth=1)

        ax[0].hlines(y0, 0, shape-1, colors='g')
        ax[0].hlines(shape-y0, 0, shape-1, colors='g')
        ax[0].vlines(y0, 0, shape-1, colors='g')
        ax[0].vlines(shape-y0, 0,shape-1, colors='g')
    
    div_size = shape/divisions
    
    x, y = np.meshgrid(np.arange(divisions[0]), np.arange(divisions[1]))
    
    img_trigger = np.zeros([2304,2304])
    
    if trigger_position.any():
        for k in trigger_position:
            xx = x.flatten()[k]
            yy = y.flatten()[k]

            x_begin = int(xx*div_size[0])
            x_end = int((xx+1)*div_size[0])

            y_begin = int(yy*div_size[1])
            y_end = int((yy+1)*div_size[1])

            x_begin = x_begin - (overlap if x_begin != 0 else 0)
            x_end = x_end + (overlap if x_end != 2304 else 0)

            y_begin = y_begin - (overlap if y_begin != 0 else 0)
            y_end = y_end + (overlap if y_end != 2304 else 0)
            
            img_trigger[x_begin:x_end, y_begin:y_end] = image[x_begin:x_end, y_begin:y_end]
    
    ax[1].imshow(img_trigger, cmap='gray', vmin=vmin, vmax=vmax)
    ax[1].grid(color='gray', linestyle='--', linewidth=1)
    ax[1].set_xticks(np.arange(0,2304,2304/12))
    ax[1].set_yticks(np.arange(0,2304,2304/12))

    plt.title ("Event: {:d} at {:s} triggered {:d} times".format(event_number, event_time, len(trigger_position)))
    
    #plt.show()
    
    return


def plot_waveform(waveform, lenw, pmt, event_number, event_time):
    import numpy as np
    
    t = np.linspace(0,lenw, lenw)
    for ipmt in range(pmt):
        plt.subplot(pmt, 2, ipmt*2+2)
        plt.plot(t, waveform[ipmt])
    return
#   fig, ax = plt.subplots(nrows=pmt, ncols=1)
#   for ipmt in range(pmt):
#       ax[ipmt].plot(t, waveform[ipmt])
#   return ax
    
def main(grid=False, vmin=DEFAULT_VMIN_VALUE, vmax=DEFAULT_VMAX_VALUE, ped=DEFAULT_PED_VALUE, 
         y0=DEFAULT_FRAME_VALUE, pmt=DEFAULT_PMT_VALUE, verbose=True):
    # Create our client
    client = midas.client.MidasClient("db_display")
    
    buffer_handle = client.open_event_buffer("SYSTEM",None,1000000000)

    request_id = client.register_event_request(buffer_handle, sampling_type = 2)
    
    plt.ion()
    fig, ax = plt.subplots(1, 2, figsize=(12,6), facecolor='#DEDEDE')

#    fig = plt.figure()

    print("Events display running..., Crtl-C to stop")
    print("Ped value, or file: "+ ped)
    if ped == DEFAULT_PED_VALUE:
        pad_varege_value = float(ped)
    print("Image range vmin: {:s}, vmax: {:s}".format(vmin, vmax))
    vmin = int(vmin)
    vmax = int(vmax)
    y0 = int(y0)
    while True:
        try:
            event = client.receive_event(buffer_handle, async_flag=False)
            if event is None:
            	continue
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

            #plt.ion() #sovrapone i grafici nella stessa finestra
            #plt.clf()
            for bank_name, bank in event.banks.items():
		
                if bank_name=='INPT':
                    slow = cy.daq_slow2array(bank) 
                    if slow is None:
                    	break
		
                if bank_name=='DGH0': 
                    waveform_header = cy.daq_dgz2header(bank)
                    if verbose: print (waveform_header)
                    waveform = cy.daq_dgz2array(event.banks['DIG0'], waveform_header)
                    lenw = waveform_header[2]

                    plot_waveform(waveform, lenw, int(pmt), event_number, event_time)

                if bank_name=='CAM0': 
                    
                    t1 = time.time()
                    img, _, _ = cy.daq_cam2array(bank)
                    
                    img_sparkless = np.copy(img)
                    coord = np.load("/home/standard/Documents/pains-test/spark_coordinates_3890.npy")
                    img_sparkless[coord[:,0], coord[:,1]] = np.mean(img)
                    
                    std_arr = find_stdArray(img_sparkless.reshape(1,2304,2304), divisions, overlap = 30)
                    threshold = np.load("/home/standard/Documents/pains-test/threshold_90.npy")
                    trigger_position = np.where(std_arr[0] > threshold)[0]
                    plot_image(ax, event.banks['CAM0'], vmin = vmin, vmax = vmax, grid = grid, event_number = event_number, event_time = event_time,  trigger_position = trigger_position, divisions = divisions, y0 = y0)
                    
                    t2 = time.time()
                    print(t2-t1)
                
            fig.canvas.flush_events()
            time.sleep(0.05)
            #plt.show()
            #plt.pause(0.01)
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
    parser.add_option('-l','--pmt', dest='pmt', action="store", type="string", default=DEFAULT_PMT_VALUE, help='show X PMT, where X is the number of channel');
    parser.add_option('-y','--y0', dest='y0', action="store", type="string", default=DEFAULT_FRAME_VALUE, help='green frame (pixel) = ' + DEFAULT_FRAME_VALUE);
    parser.add_option('-v','--verbose', dest='verbose', action="store_true", default=False, help='verbose output;');
    (options, args) = parser.parse_args()
    main(grid=options.grid, vmin=options.vmin, vmax=options.vmax,  ped=options.ped, y0=options.y0, pmt=options.pmt, verbose=options.verbose)


