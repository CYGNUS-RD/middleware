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
from scipy.signal import find_peaks
from scipy.optimize import curve_fit
#import pre_reconstruction as pr
import time

import matplotlib

import midas
import midas.client
import sys

DEFAULT_PED_VALUE = '100'
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
#    plt.isinteractive()
    #plt.ion()
    #plt.show(block=False)
    #plt.pause(0.05)
    

# ============================ new ==============================

def moving_average(a, n=3) :
    ret = np.cumsum(a, dtype=float)
    ret[n:] = ret[n:] - ret[:-n]
    return ret[n - 1:] / n

def getPeaks(z, discarded = 200, Lmax = 2304, sep = 100, norm = False):
    
    z = z.T
    allPeaks     = []
    allPeakProps = {}
    propsInit = False
    
    if not norm: normz = 1
    else: normz = np.max(z)
    normz = 1
            
    www = 610
    minP, maxP = 1152-www-discarded-24, 1152+www-discarded - 24
    
    for l in np.arange(600, 1705, sep):
    #for l in np.arange(1600, 1705, sep):
        
        y0 = l
        yyy = z[:,y0]/normz

        yyy = yyy + z[:,y0+1]/normz
        yyy = yyy + z[:,y0+2]/normz
        yyy = yyy + z[:,y0+3]/normz
        yyy = yyy + z[:,y0+4]/normz
        yyy = yyy + z[:,y0-1]/normz
        yyy = yyy + z[:,y0-2]/normz
        yyy = yyy + z[:,y0-3]/normz
        yyy = yyy + z[:,y0-4]/normz
        yyy = yyy /9


        yyy = yyy[discarded:(Lmax - discarded)]
        yyyma = moving_average(yyy, 3)

        yyyma2 = moving_average(yyy, 51)

        yyysub = yyyma[24:-24] - yyyma2

    #     sos = signal.butter(10, 0.1, 'hp', fs=1000, output='sos')
    #     filtered = signal.sosfilt(sos, yyyma)

    #     peaks, properties = find_peaks(-filtered, height=-500, distance = 180, width = 2, prominence = 2)
        peaks, properties = find_peaks(-yyysub, height=-1500/normz, distance = 120, width = 2, prominence = 2/normz)
        
        
        #fig = plt.figure()
        #plt.plot(-yyysub)
        #plt.show()
        #print(-yyysub)
        #print("===================")
        #print(np.mean(yyysub))
        #time.sleep(3)
        #raise Exception("DEBUG")
        
        peaks2  = peaks[np.where((peaks>minP) & (peaks < maxP))]
        properties2 = {}
        
        for kk in properties.keys():
            properties2[kk] = properties[kk][np.where((peaks>minP) & (peaks < maxP))]
        
        if not propsInit:
            for kk in properties2.keys():
                allPeakProps[kk] = []
            propsInit = True
        
        #print(len(peaks2))
        if len(peaks2)== 6:
            for pe in peaks2:
                allPeaks.append([pe+discarded+24, y0])

            for kk in properties2.keys():
                for jj, pe in enumerate(peaks2):
                    allPeakProps[kk].append(properties2[kk][jj])
    
    allPeaks = np.array(allPeaks)
    for kk in allPeakProps.keys():
        allPeakProps[kk] = np.array(allPeakProps[kk])
    
    return allPeaks, allPeakProps

def getFscore(peaks, properties):
    if len(peaks) == 0: return -111
    #print(peaks)
    #print(properties.keys())
    rows = []
    for i in range(6):
        rows.append(properties['peak_heights'][np.where(np.abs(peaks[:, 0] - peaks[i, 0]) < 50)])
    
    #print(rows[2])
    #print(rows[3])
    return np.mean(rows[2])+np.mean(rows[3]) #+ np.mean(rows[1])+np.mean(rows[4])


def Line(x, m, c):
    return m*x + c

def getHscore(peaks, properties, imgdim = 2304):
    if len(peaks) == 0: return -111
    #print(peaks)
    #print(properties.keys())
    rows = []
    for i in range(6):
        rows.append(peaks[np.where(np.abs(peaks[:, 0] - peaks[i, 0]) < 50)])
    
    poss = []

    for r in rows:
        xx = r[:, 0]
        yy = r[:, 1]
    
        poss.append([np.mean(yy), np.mean(xx)])
    
    poss  = np.array(poss)
    
    yyyy = poss[:, 1]-imgdim/2
    xxxx = np.arange(0, len(yyyy), 1)
    
    optl, pcovl = curve_fit(Line, xxxx, yyyy)
    
    return np.abs(-2.5-optl[1]/optl[0])


def parabole(x, a, b, c):
    return a + b*x + c**2

def getVscore(peaks, properties, imgdim = 2304):
    if len(peaks) == 0: return -111
    rows = []
    for i in range(6):
        rows.append(peaks[np.where(np.abs(peaks[:, 0] - peaks[i, 0]) < 50)])
    
    r2i = []
    r4i = []

    r2f = []
    r4f = []
    
    for i, r in enumerate(rows):
        xx = r[:, 0]
        yy = r[:, 1]
    
        #opt, pcov = curve_fit(parabole, yy, xx)
        opt, pcov = curve_fit(Line, yy, xx)
        
        xline = np.arange(int(imgdim/2) - 600, int(imgdim/2)+600)
        
        
        #yline = parabole(xline, opt[0], opt[1], opt[2])
        yline = Line(xline, opt[0], opt[1])#
        
        if i==1:
            r2i.append([xline[0], yline[0]])
            r2f.append([xline[-1], yline[-1]])
        elif i ==3:
            r4i.append([xline[0], yline[0]])
            r4f.append([xline[-1], yline[-1]])
            
    diffi = r2i[0][1] - r4i[0][1]#/(r2i[0][1] + r4i[0][1])
    difff = r2f[0][1] - r4f[0][1]#/(r2f[0][1] + r4f[0][1])

    return (diffi - difff)*100/(diffi + difff)


def image_plot2(bank, vmin, vmax, grid, event_number, event_time, pedarr_fr, y0=DEFAULT_FRAME_VALUE):

    shape = int(np.sqrt(bank.size_bytes*8/16))
    image = np.reshape(bank.data, (shape, shape))
    
    plt.clf()
    im = plt.imshow(image-pedarr_fr, cmap='gray', vmin=vmin, vmax=vmax)

    peaks, properties = getPeaks(image, sep = 50, norm = False)
    
    FScore = getFscore(peaks, properties)
    HScore = getHscore(peaks, properties)
    VScore = getVscore(peaks, properties)
    
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
    
    if len(peaks!=0): plt.scatter(peaks[:,0], peaks[:,1], marker = 'x', color = 'red')
    plt.title ("Event: {:d} at {:s} - Fscore: {:.1f} - Hscore: {:.3f} - Vscore: {:.3f}".format(event_number, event_time, FScore, HScore, VScore))
#    plt.isinteractive()
    #plt.ion()
    #plt.show(block=False)
    #plt.pause(0.05)
    


def loadped(pedarr_fr, exposure_time):
    exposure_time_old = exposure_time
    if not len(pedarr_fr):
        try:
            print("Loading ped file")
            pedarr_fr = np.load("pedarr_%.1f.npy" % exposure_time)
        except:
            print("Using fixed ped = 99")
            pedarr_fr = 99*np.ones((2304,2304),dtype=int)
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
                
                image_plot2(event.banks['CAM0'], vmin, vmax, grid, event_number, event_time, pedarr_fr, y0)
                
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

