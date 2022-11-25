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
import multiprocess

MAX_CPU_AVAILABLE   = multiprocess.cpu_count()
DAQ_ROOT            = os.environ['DAQ_ROOT']
DEFAULT_PATH_ONLINE = DAQ_ROOT+'/online/'

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

def run_reco(image, run_number, ev_number, pedarr_fr, sigarr_fr, nsigma, verbose):
    arr = image
    ## Include some reconstruction code here
    #
    t1 = time.time()
    values = pr.pre_reconstruction(arr, run_number, ev_number, pedarr_fr, sigarr_fr, nsigma, printtime=verbose)
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
    
def recoAndUpdate(image, run_number, event_number, pedarr_fr, sigarr_fr, nsigma, timestamp, connection, verbose=False):
    #table_name = "Run{:05d}".format(run_number)
    table_name = "RecoTable"
    df = run_reco(image, run_number, event_number, pedarr_fr, sigarr_fr, nsigma, verbose)
    if verbose: print("[Sending reco variables to SQL]")
    df.insert(loc=0, column='timestamp', value = timestamp)
    try:
        push_panda_table_sql(connection, table_name, df)
    except:
        print["Connection down, SQL not sent"]
        
    if verbose: print("[SQL sent]")
    #df.to_sql("Run10000", con=connection, if_exists='append', index_label='id')

def main(verbose=True):

    client = midas.client.MidasClient("middleware")
    buffer_handle = client.open_event_buffer("SYSTEM",None,1000000000)
    request_id = client.register_event_request(buffer_handle)
    
    # init program variables
    t0 = time.time()
    vmin         = 95
    vmax         = 130
    pedarr_fr    = []
    #ped_array    = []
    ped_id       = 0
    ped_date_max = 10
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

    # global run useful varibles
    header_environment = client.odb_get("/Equipment/Environment/Settings/Names Input")
    header_environment = header_event + header_environment

    # DEBUG VARABLE
    t0bc = time.time()
    t1bc = time.time()
    
    while True:

        event = client.receive_event(buffer_handle, async_flag=True)

        state         = client.odb_get("/Runinfo/State")
        gem_hv_state  = client.odb_get("/Equipment/HV/Variables/ChState[0]")
        exposure_time = client.odb_get("/Configurations/Exposure")
        
        if event is not None:
            t0b = time.time()
            if event.header.is_midas_internal_event():
                if verbose:
                    print("Saw a special event")
                continue

            # global event useful variables
            bank_names    = ", ".join(b.name for b in event.banks.values())
            event_info    = [event.header.timestamp, event.header.serial_number, event.header.event_id]
            free_running  = client.odb_get("/Configurations/FreeRunning")
            run_number    = client.odb_get("/Runinfo/Run number")
            nsigma        = client.odb_get("/middleware/nsigma")
            event_number  = event.header.serial_number
            event_time    = datetime.fromtimestamp(event.header.timestamp).strftime('%Y-%m-%d %H:%M:%S')

            if verbose:
                print("Event # %s of type ID %s contains banks %s" % (event.header.serial_number, event.header.event_id, bank_names))
                print("Received event with timestamp %s containing banks %s" % (event.header.timestamp, bank_names))
                print("%s, banks %s" % (datetime.utcfromtimestamp(event.header.timestamp).strftime('%Y-%m-%d %H:%M:%S'), bank_names))


            #if event is not None:

            start = time.perf_counter()
            if 'CAM0' in bank_names:

                t0bc = time.time()
                if init_cam: # chiedere a francesco se possiamo metterlo nel DB e rimuovere questo pezzo
                    shape_image = int(np.sqrt(event.banks['CAM0'].size_bytes*8/16))
                    m_image = np.zeros((shape_image, shape_image), dtype=np.float64)
                    s_image = np.zeros((shape_image, shape_image), dtype=np.float64)
                    if verbose: print("image shape: "+str(shape_image)) 
                    init_cam = False 

                image = np.reshape(event.banks['CAM0'].data, (shape_image, shape_image))
                t1bc = time.time() 

                ## Save image
                t1 = time.time()
                image_update_time = client.odb_get("/middleware/image_update_time")
                if (t1-t0) > image_update_time:
                    print("[Saving image for presenter]")
                    #saveimege = multiprocess.Process(target=image_jpg, args=(image, vmin, vmax, event_number, event_time,))
                    #saveimege.daemon = True
                    #saveimege.start()
                    image_jpg(image, vmin, vmax, event_number, event_time)
                    t0 = time.time()

                ## Skipping spark images
                if skipSpark(image):
                    continue

                if not gem_hv_state and state == midas.STATE_RUNNING:
                    if verbose: print("[Storing ped data {:d} images]".format(ped_id))
                    #ped_array.append(image)
                    
                    m_image += image
                    s_image += image**2
                    
                    exposure_ped = exposure_time
                    ped_id+= 1
                    
                elif gem_hv_state and state == midas.STATE_RUNNING:
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

                    if verbose: print("[Starting analysis Image {:d}]".format(event.header.serial_number))
                    reconstruction_sample_gap = client.odb_get("/middleware/reconstruction_sample_gap")    
                    if (event_number%reconstruction_sample_gap) == 0:
                        recoAndUpdate(image, run_number, event_number, pedarr_fr, sigarr_fr, 
                                  nsigma, event.header.timestamp, connection, verbose)
#                         savereco = multiprocess.Process(target=recoAndUpdate, args=(image, run_number, event_number, pedarr_fr,
#                                                                                     sigarr_fr, nsigma, event.header.timestamp,
#                                                                                     connection, verbose,))
#                         savereco.daemon = True
#                         savereco.start()

            t1b = time.time()    
            if 'DGH0' in bank_names:

                waveform_header = cy.daq_dgz2header(event.banks['DGH0'])
                if verbose: print (waveform_header)
                waveform = cy.daq_dgz2array(event.banks['DIG0'], waveform_header)
                lenw = waveform_header[2]

            t2b = time.time()
            if 'INPT' in bank_names:                
                value = [event_info + list(event.banks['INPT'].data)]
                if verbose:
                    print(value)
                    print("........")
                    print(header_environment)

                de = pd.DataFrame(value, columns = header_environment)
                table_name_sc = "SlowControl"
                push_panda_table_sql(connection,table_name_sc, de)          

            t3b = time.time()
            end = time.perf_counter()
            print("Run: {:d} Event: {:d} at {:s}".format(run_number, event_number, event_time))
            print("Elapsed, slow {:.2f}, pmt {:.2f}, cam {:.2f}, read cam {:.2f}, subprocess {:.2f} ".format(t3b-t2b, t2b-t1b, t1b-t0b, t1bc-t0bc, end-start) )
        save_ped = client.odb_get("/middleware/save_ped")
        if save_ped and (ped_id > 0):
            print("[Making Pedestal over {:d} images]".format(ped_id))
            #pedarr_fr, sigarr_fr = makeped(ped_array)
            pedarr_fr = m_image/ped_id
        
            sigarr_fr = np.sqrt((s_image - pedarr_fr**2 * ped_id) / (ped_id - 1))
            #m_image[np.isnan(s_image)==True]=m_image.mean() # pach per i valori insani di sigma e media
            #s_image[np.isnan(s_image)==True]=1024
            np.save(DEFAULT_PATH_ONLINE+"pedarr_%.1f.npy" % exposure_ped, pedarr_fr)
            np.save(DEFAULT_PATH_ONLINE+"sigarr_%.1f.npy" % exposure_ped, sigarr_fr)

            ped_id = 0
            m_image = np.zeros((shape_image, shape_image), dtype=np.float64)
            s_image = np.zeros((shape_image, shape_image), dtype=np.float64)
            client.odb_set("/middleware/save_ped", False)
            if verbose: print("[Pedestal done]")
        client.communicate(10)
        time.sleep(0.1)
        

    client.deregister_event_request(buffer_handle, request_id)

    client.disconnect()
    
        
if __name__ == "__main__":
    from optparse import OptionParser
    parser = OptionParser(usage='usage: %prog\t ')
    parser.add_option('-v','--verbose', dest='verbose', action="store_true", default=False, help='verbose output;');
    (options, args) = parser.parse_args()
    main(verbose=options.verbose)
