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
DEFAULT_PMT_FAST_VALUE   = '4'
DEFAULT_PMT_SLOW_VALUE   = '5'


def plot_iamge(bank, vmin, vmax, grid, event_number, event_time, y0=DEFAULT_FRAME_VALUE):

    test_size=bank.size_bytes*8/16/(5308416)      #5308416=2304*2304
    if test_size<1.1:

        #Fusion,Flash
        shapex = shapey = int(np.sqrt(bank.size_bytes*8/16))
    else:
        #quest
        shapex=4096
        shapey=2304
        vmin=195
        vmax=220

    image = np.reshape(bank.data, (shapey, shapex))

    ax = plt.imshow(image, cmap='gray', vmin=vmin, vmax=vmax)


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
    return

def plot_waveform(waveform_f, waveform_sl, lenw_f, lenw_sl, pmt_f, pmt_sl, event_number, event_time):
    import numpy as np
    
    t = np.linspace(0,lenw_f, lenw_f)
    for ipmt in range(pmt_f):
        plt.subplot(pmt_f+pmt_sl, 2, ipmt*2+2)
        plt.plot(t, waveform_f[ipmt])
    
    t = np.linspace(0,lenw_sl, lenw_sl)    
    for ipmt in range(pmt_sl):
        plt.subplot(pmt_f+pmt_sl, 2, 2*(pmt_f)+ipmt*2+2)
        #plt.xlim(0,lenw_f)
        plt.plot(t, waveform_sl[ipmt])
        
    return
#   fig, ax = plt.subplots(nrows=pmt, ncols=1)
#   for ipmt in range(pmt):
#       ax[ipmt].plot(t, waveform[ipmt])
#   return ax
    
def main(grid=False, vmin=DEFAULT_VMIN_VALUE, vmax=DEFAULT_VMAX_VALUE, ped=DEFAULT_PED_VALUE, 
         y0=DEFAULT_FRAME_VALUE, pmt_f=DEFAULT_PMT_FAST_VALUE, pmt_sl=DEFAULT_PMT_SLOW_VALUE, verbose=False):
    # Create our client
    client = midas.client.MidasClient("db_display")
    
    buffer_handle = client.open_event_buffer("SYSTEM",None,1000000000)

    request_id = client.register_event_request(buffer_handle, sampling_type = 2)
    
    plt.ion()
    fig = plt.figure(figsize=(12,6), facecolor='#DEDEDE')

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
            corrected = client.odb_get("/Configurations/DRS4Correction")
            channels_offset = client.odb_get("/Configurations/DigitizerOffset")

            if verbose:
                print("Event # %s of type ID %s contains banks %s" % (event_number, event.header.event_id, bank_names))
                print("Received event with timestamp %s containing banks %s" % (event.header.timestamp, bank_names))
                print("%s, banks %s" % (event_time, bank_names))

            #plt.ion() #sovrapone i grafici nella stessa finestra
            
            for bank_name, bank in event.banks.items():
		
                if bank_name=='INPT':
                    slow = cy.daq_slow2array(bank) 
                    if slow is None:
                    	break
		
                if bank_name=='DGH0': 
                    plt.clf()
                    waveform_header = cy.daq_dgz_full2header(bank, verbose=False)
                    if verbose: print (waveform_header)
                    waveform_fast, waveform_slow = cy.daq_dgz_full2array(event.banks['DIG0'], waveform_header, verbose=False, corrected=corrected,ch_offset=channels_offset)
                    lenw_fast = waveform_header[2][0]
                    lenw_slow = waveform_header[2][1]

                    plot_waveform(waveform_fast, waveform_slow, lenw_fast, lenw_slow, int(pmt_f), int(pmt_sl), event_number, event_time)
                    

                if bank_name=='CAM0': 
                    if client.odb_get("/Configurations/FreeRunning") == False:
                       plt.subplot(1,2,1)
                    else: 
                       plt.clf()
                    t1 = time.time()
                    plot_iamge(event.banks['CAM0'], vmin, vmax, grid, event_number, event_time, y0)
                    t2 = time.time()
                    
                    print(t2-t1)
                
            
            plt.title ("Event: {:d} at {:s}".format(event_number, event_time))
            fig.canvas.draw()
            fig.canvas.flush_events()
            time.sleep(0.03)
            #plt.show()
            #plt.pause(0.01)
            client.communicate(10)
        except KeyboardInterrupt:
            client.deregister_event_request(buffer_handle, request_id)
            client.disconnect()
            print ("\nBye, bye...")
            sys.exit()

    
    
if __name__ == "__main__":
#    from optparse import OptionParser
#    parser = OptionParser(usage='usage: %prog\t ')
#    parser.add_option('-g','--grid', dest='grid', action="store_true", default=False, help='grid;');
#    parser.add_option('-n','--vmin', dest='vmin', action="store", type="string", default=DEFAULT_VMIN_VALUE, help='vmin, dafaul = ' + DEFAULT_VMIN_VALUE);
 #    parser.add_option('-m','--vmax', dest='vmax', action="store", type="string", default=DEFAULT_VMAX_VALUE, help='vman, dafaul = ' + DEFAULT_VMAX_VALUE);
#    parser.add_option('-p','--ped', dest='ped', action="store", type="string", default=DEFAULT_PED_VALUE, help='pedestal file path, if none 99 value assumed for all points;');
#    parser.add_option('-l','--pmt', dest='pmt', action="store", type="string", default=DEFAULT_PMT_FAST_VALUE, help='show X PMT, where X is the number of channel');		#a bit broken function (do not use it unless you accept risks)
#    parser.add_option('-y','--y0', dest='y0', action="store", type="string", default=DEFAULT_FRAME_VALUE, help='green frame (pixel) = ' + DEFAULT_FRAME_VALUE);
#    parser.add_option('-v','--verbose', dest='verbose', action="store_true", default=False, help='verbose output;');
#    (options, args) = parser.parse_args()
#    main(grid=options.grid, vmin=options.vmin, vmax=options.vmax,  ped=options.ped, y0=options.y0, pmt_f=options.pmt_f,pmt_sl=options.pmt_sl, verbose=options.verbose)
 main()


