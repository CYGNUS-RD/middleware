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
import pre_reconstruction as pr
import time
import pandas as pd

import midas
import midas.client

import mysql.connector

import sys
import cygno as cy

DEFAULT_PATH_ONLINE = '/home/standard/daq/online/'

def image_jpg(image, vmin, vmax, event_number, event_time):
    
    im = plt.imshow(image, cmap='gray', vmin=vmin, vmax=vmax)
    plt.title ("Event: {:d} at {:s}".format(event_number, event_time))
    plt.savefig(DEFAULT_PATH_ONLINE+'custom/tmp.png')
    return 

def makeped(ped_array):
    #print(np.shape(ped_array))
    
    pedarr_fr = np.mean(ped_array, axis=0)
    sigarr_fr = np.std(ped_array, axis=0)
    #print(pedarr_fr[1:100,1])
    return np.array(pedarr_fr), np.array(sigarr_fr)

def run_reco(image, run_number, ev_number, pedarr_fr, sigarr_fr, nsigma):
    arr = image
    ## Include some reconstruction code here
    #
    t1 = time.time()
    values = pr.pre_reconstruction(arr, run_number, ev_number, pedarr_fr, sigarr_fr, nsigma, printtime=True)
    t2 = time.time()
    df = pr.create_pandas(values)
    return df

def push_panda_table_sql(connection, table_name, df):
    
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
        mycursor.execute(sql, tuple(row.astype(str)))
        connection.commit()

    mycursor.close()


def skipSpark(image):
    
    sparktest = False
    
    integralImage = sum(sum(image))
    sizeX = np.shape(image)[0]
    sizeY = np.shape(image)[1]
    
    testspark     = 100*sizeX*sizeY+9000000
    
    if integralImage > testspark:
        print("Image has spark, will not be analyzed!")
        sparktest = True
    
    
    return sparktest
    
    

def main(verbose=True):

    client = midas.client.MidasClient("middleware")
    buffer_handle = client.open_event_buffer("SYSTEM",None,1000000000)
    request_id = client.register_event_request(buffer_handle)
    
    # init program variables
    vmin         = 95
    vmax         = 130
    pedarr_fr    = []
    ped_array    = []
    ped_id       = 0
    ped_date_max = 10
    aux_hv       = 1
    init_cam     = True
    header_event = [
        'timestamp',
        'serial_number',
        'event_id']
    # init sql variabile and connector
    connection = mysql.connector.connect(
      host=os.environ['MYSQL_IP'],
      user=os.environ['MYSQL_USER'],
      password=os.environ['MYSQL_PASSWORD'],
      database=os.environ['MYSQL_DATABASE'],
      port=int(os.environ['MYSQL_PORT'])
    )

#    mycursor = connection.cursor()


    # global run useful varibles
    header_environment = client.odb_get("/Equipment/Environment/Settings/Names Input")
    header_environment = header_event + header_environment
    t0 = time.time()
    t0bc = time.time()
    t1bc = time.time()
    while True:
        
        event = client.receive_event(buffer_handle, async_flag=False)
        if event.header.is_midas_internal_event():
            if verbose:
                print("Saw a special event")
            continue
   
        # global event useful variables
        bank_names    = ", ".join(b.name for b in event.banks.values())
        event_info    = [event.header.timestamp, event.header.serial_number, event.header.event_id]
        gem_hv_state  = client.odb_get("/Equipment/HV/Variables/ChState[0]")
        free_running  = client.odb_get("/Configurations/FreeRunning")
        exposure_time = client.odb_get("/Configurations/Exposure")
        run_number    = client.odb_get("/Runinfo/Run number")
        nsigma        = client.odb_get("/Logger/Runlog/SQL/nsigma")
        if verbose:
            print("Event # %s of type ID %s contains banks %s" % (event.header.serial_number, event.header.event_id, bank_names))
            print("Received event with timestamp %s containing banks %s" % (event.header.timestamp, bank_names))
            print("%s, banks %s" % (datetime.utcfromtimestamp(event.header.timestamp).strftime('%Y-%m-%d %H:%M:%S'), bank_names))

        
# da ricontrollare, la logica non funziona in modo combinato 
   
        #if event is not None:
        t0b = time.time()
        if 'CAM0' in bank_names:
            

            t0bc = time.time()
            if init_cam: # chiedere a francesco se possiamo metterlo nel DB e rimuovere questo pezzo
                shape_image = int(np.sqrt(event.banks['CAM0'].size_bytes*8/16))
                if verbose: print("image shape: "+str(shape_image)) 
                init_cam = False 
                
            image = np.reshape(event.banks['CAM0'].data, (shape_image, shape_image))
            if verbose: print(image)
            ## Save image
            event_number = event.header.serial_number
            event_time = datetime.fromtimestamp(event.header.timestamp).strftime('%Y-%m-%d %H:%M:%S')
            t1bc = time.time() 
            
            t1 = time.time()
            if (t1-t0) > 10:
                print("[Saving image for presenter]")
                image_jpg(image, vmin, vmax, event_number, event_time)
                t0 = time.time()
            
            ## Skipping spark images
            if skipSpark(image):
                continue

            if not gem_hv_state:
                if verbose: print("[Storing ped data {:d} images]".format(ped_id))
                ped_array.append(image)
                ped_id+= 1
                aux_hv = 0
            else:
                if not aux_hv:
                    if verbose: print("[Making Pedestal over {:d} images]".format(ped_id))
                    pedarr_fr, sigarr_fr = makeped(ped_array)
                    np.save(DEFAULT_PATH_ONLINE+"pedarr_%.1f.npy" % exposure_time, pedarr_fr)
                    np.save(DEFAULT_PATH_ONLINE+"sigarr_%.1f.npy" % exposure_time, sigarr_fr)
                    
                    ped_id = 0
                    aux_hv = 1
                    # in realta' il ped andrebbe azzerato altrove solo al cambio di stato
                    ped_array    = []
                    if verbose: print("[Pedestal done]")
                else:
                    if verbose: print("[Initiating Reconstruction]")
                    if not len(pedarr_fr):
                        if verbose: print("[Loading Pedestal]")
                        pedarr_fr = np.load(DEFAULT_PATH_ONLINE+"pedarr_%.1f.npy" % exposure_time)
                        sigarr_fr = np.load(DEFAULT_PATH_ONLINE+"sigarr_%.1f.npy" % exposure_time)
                        ## Checking oldness of pedestal file
                        fileStatsObj     = os.stat (DEFAULT_PATH_ONLINE+"pedarr_%.1f.npy" % exposure_time)
                        modificationTime = time.ctime(fileStatsObj[stat.ST_MTIME])
                        oldness = (time.time() - fileStatsObj[stat.ST_MTIME])/(60*60*24)

                        print("Last Modified Time: ", modificationTime )
                        print("Oldness of file: %.2f days" % oldness)
                        if oldness > ped_date_max:
                            print("You are using Pedestal file created more than %d days ago" % ped_date_max)
                            print("You should think of recreating it")
                    
                    
                    
                    #print(image[1:100,1])
                    if verbose: print("[Starting analysis Image {:d}]".format(event.header.serial_number))

                    #table_name = "Run{:05d}".format(run_number)
                    table_name = "RecoTable"
                    
                    df = run_reco(image, run_number, event.header.serial_number, pedarr_fr, sigarr_fr, nsigma)
                    if verbose: print("[Sending reco variables to SQL]")
                    df.insert(loc=0, column='timestamp', value = event.header.timestamp)
                    push_panda_table_sql(connection, table_name, df)
                    if verbose: print("[SQL sent]")
                    #df.to_sql("Run10000", con=connection, if_exists='append', index_label='id')
        t1b = time.time()    
        if 'DGH0' in bank_names:
            
            waveform_header = cy.daq_dgz2header(event.banks['DGH0'])
            if verbose: print (waveform_header)
            waveform = cy.daq_dgz2array(event.banks['DIG0'], waveform_header)
            lenw = waveform_header[2]

        t2b = time.time()
        if 'INPT' in bank_names:
            if verbose:
                print(datetime.utcfromtimestamp(event.header.timestamp).strftime('%Y-%m-%d %H:%M:%S'), 
                  "event: "+str(event.header.serial_number))
                print("  >>>  Entry in bank %s is %s" % (bank_names, event.banks['INPT'].data))
                
            value = [event_info + list(event.banks['INPT'].data)]
            if verbose:
                print(value)
                print("........")
                print(header_environment)
                
            de = pd.DataFrame(value, columns = header_environment)
            table_name_sc = "SlowControl"
            push_panda_table_sql(connection,table_name_sc, de)          
        t3b = time.time()
        print("Elapsed, slow {:.2f}, pmt {:.2f}, cam {:.2f}, cam part {:.2f}: ".format(t3b-t2b, t2b-t1b, t1b-t0b, t1bc-t0bc) )
       # Talk to midas so it knows we're alive, or can kill us if the user
        # pressed the "stop program" button.
        client.communicate(10)
        
    # You don't have to cancel the event request manually (it will be done
    # automatically when the program exits), but for completeness we're just
    # showing that such a function exists.
    client.deregister_event_request(buffer_handle, request_id)
    # plt.show()
    
    # Disconnect from midas before we exit.
    # mycursor.close()
    client.disconnect()
    
        
if __name__ == "__main__":
    from optparse import OptionParser
    parser = OptionParser(usage='usage: %prog\t ')
    parser.add_option('-v','--verbose', dest='verbose', action="store_true", default=False, help='verbose output;');
    (options, args) = parser.parse_args()
    main(verbose=options.verbose)
