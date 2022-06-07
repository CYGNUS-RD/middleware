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

    client = midas.client.MidasClient("db_producer_v0.1")
    buffer_handle = client.open_event_buffer("SYSTEM",None,1000000000)
    request_id = client.register_event_request(buffer_handle)
    
    # init program variables
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
    
    while True:
        
        event = client.receive_event(buffer_handle, async_flag=False)
        if event.header.is_midas_internal_event():
            if verbose:
                print("Saw a special event")
            continue
   
        # global event useful variables
        bank_names   = ", ".join(b.name for b in event.banks.values())
        event_info   = [event.header.timestamp, event.header.serial_number, event.header.event_id]
        gem_hv_state = client.odb_get("/Equipment/HV/Variables/ChState[0]")
        free_running = client.odb_get("/Configurations/FreeRunning")
        run_number   = client.odb_get("/Runinfo/Run number")
        nsigma       = client.odb_get("/Logger/Runlog/SQL/nsigma")
        if verbose:
            print("Event # %s of type ID %s contains banks %s" % (event.header.serial_number, event.header.event_id, bank_names))
            print("Received event with timestamp %s containing banks %s" % (event.header.timestamp, bank_names))
            print("%s, banks %s" % (datetime.utcfromtimestamp(event.header.timestamp).strftime('%Y-%m-%d %H:%M:%S'), bank_names))

        
# da ricontrollare, la logica non funziona in modo combinato 
   
        #if event is not None:
        if bank_names=='CAM0':
            
            if init_cam: # chiedere a francesco se possiamo metterlo nel DB e rimuovere questo pezzo
                shape_image = int(np.sqrt(event.banks['CAM0'].size_bytes*8/16))
                if verbose: print("image shape: "+str(shape_image)) 
                init_cam = False 
                
            image = np.reshape(event.banks['CAM0'].data, (shape_image, shape_image))
            
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
                    np.save("pedarr.npy",pedarr_fr)
                    np.save("sigarr.npy",sigarr_fr)
                    
                    ped_id = 0
                    aux_hv = 1
                    # in realta' il ped andrebbe azzerato altrove solo al cambio di stato
                    ped_array    = []
                    if verbose: print("[Pedestal done]")
                else:
                    if verbose: print("[Initiating Reconstruction]")
                    if not len(pedarr_fr):
                        if verbose: print("[Loading Pedestal]")
                        pedarr_fr = np.load("pedarr.npy")
                        sigarr_fr = np.load("sigarr.npy")
                        ## Checking oldness of pedestal file
                        fileStatsObj     = os.stat ("pedarr.npy")
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
            
        if bank_names=='DGH0':
            
            nboard = event.banks['DGH0'].data[0]
            ich = 1
            data_offset = 0
            Waveform = []
            for iboard in nboard:
                name_board = event.banks['DGH0'].data[ich]
                ich+=1
                sample_number = event.banks['DGH0'].data[ich]
                ich+=1
                channels_number =  event.banks['DGH0'].data[ich]
                ich+=1
                number_events = event.banks['DGH0'].data[ich]
                ich+=1
                vertical_resulution = event.banks['DGH0'].data[ich]
                ich+=1
                sampling_rate = event.banks['DGH0'].data[ich]
                for icahnnels in channels_number:
                    ich+=1
                    cannaels_offset[icahnnels] = event.banks['DGH0'].data[ich]
                    
                for ievent in number_events:
                    for icahnnels in channels_number:
                        start = data_offset 
                        Waveform[ievent, ichannels] = event.banks['DIG0'].data[data_offset:data_offset+sample_number]
                        data_offset += sample_number

#             Waveform=[]
#             for i in range(ndgtz):
#                 Waveform.append(event.banks['DIG0'].data[i])
#             x=np.arange(ndgtz)
#            Waveform1 = event.banks['DIG0'].data[:ndgtz]

            
        if bank_names=='INPT':
            print(datetime.utcfromtimestamp(event.header.timestamp).strftime('%Y-%m-%d %H:%M:%S'), 
                  "event: "+str(event.header.serial_number))
            print("  >>>  Entry in bank %s is %s" % (bank_names, event.banks['INPT'].data))
            value = [event_info + list(event.banks['INPT'].data)]
            print(value)
            print("........")
            print(header_environment)
            de = pd.DataFrame(value, columns = header_environment)
            table_name_sc = "SlowControl"
            push_panda_table_sql(connection,table_name_sc, de)
#            sql = "INSERT INTO `environment` ("+" ".join(["`"+hed+"`," for hed in header_event])[:-1]+") VALUES ("+",".join([str(x) for x in value])+" )"
            # print (sql)
#            mycursor = connection.cursor()
#            mycursor.execute(sql)
#            connection.commit()
#            print(mycursor.rowcount, "Record inserted successfully into Laptop table")
            


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
