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
from cygno import cmd
#import multiprocess
import midas.file_reader

#MAX_CPU_AVAILABLE   = multiprocess.cpu_count()
#DAQ_ROOT            = os.environ['DAQ_ROOT']
DEFAULT_PATH_ONLINE = 'pedestals/' #DAQ_ROOT+'/online/'
URL                 = 'https://minio.cloud.infn.it/'

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

def ped_reco(image, run_number, ev_number, verbose):
    import pandas as pd
    
    arr = image
    ## Include some reconstruction code here
    #
    integralT = np.sum(arr)
    mediaT = np.mean(arr)
    sigmaT = np.std(arr)
    
    mediaR1 = np.mean(arr[0:256, 0:256])
    sigmaR1 = np.std(arr[0:256, 0:256])
    
    mediaR2 = np.mean(arr[int(2304/2-128):int(2304/2+128), 0:256])
    sigmaR2 = np.std(arr[int(2304/2-128):int(2304/2+128), 0:256])
    
    mediaR3 = np.mean(arr[2304-256:2304, 0:256])
    sigmaR3 = np.std(arr[2304-256:2304, 0:256])
    
    mediaR4 = np.mean(arr[0:256, int(2304/2-128):int(2304/2+128)])
    sigmaR4 = np.std(arr[0:256, int(2304/2-128):int(2304/2+128)])
    
    mediaR5 = np.mean(arr[int(2304/2-128):int(2304/2+128), int(2304/2-128):int(2304/2+128)])
    sigmaR5 = np.std(arr[int(2304/2-128):int(2304/2+128), int(2304/2-128):int(2304/2+128)])
    
    mediaR6 = np.mean(arr[2304-256:2304, int(2304/2-128):int(2304/2+128)])
    sigmaR6 = np.std(arr[2304-256:2304, int(2304/2-128):int(2304/2+128)])
    
    mediaR7 = np.mean(arr[0:256, 2304-256:2304])
    sigmaR7 = np.std(arr[0:256, 2304-256:2304])
    
    mediaR8 = np.mean(arr[int(2304/2-128):int(2304/2+128), 2304-256:2304])
    sigmaR8 = np.std(arr[int(2304/2-128):int(2304/2+128), 2304-256:2304])
    
    mediaR9 = np.mean(arr[2304-256:2304, 2304-256:2304])
    sigmaR9 = np.std(arr[2304-256:2304, 2304-256:2304])
    
    
    # initialize list of lists
    data = [run_number, ev_number, integralT, mediaT, sigmaT, mediaR1, sigmaR1, mediaR2, sigmaR2, mediaR3, sigmaR3, mediaR4, sigmaR4, mediaR5, sigmaR5, mediaR6, sigmaR6, mediaR7, sigmaR7, mediaR8, sigmaR8, mediaR9, sigmaR9]
    
    # Create the pandas DataFrame
    df = pd.DataFrame([data], columns = ['Run','Event','IntegralT','MediaT','SigmaT','MediaR1','SigmaR1','MediaR2','SigmaR2','MediaR3','SigmaR3','MediaR4','SigmaR4','MediaR5','SigmaR5','MediaR6','SigmaR6','MediaR7','SigmaR7','MediaR8','SigmaR8','MediaR9','SigmaR9'])
    
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

def recoPedAndUpdate(image, run_number, event_number, timestamp, connection, verbose=False):
    #table_name = "Run{:05d}".format(run_number)
    table_name = "PedRecoTable"
    df = ped_reco(image, run_number, event_number, verbose)
    if verbose: print("[Sending reco variables to SQL]")
    df.insert(loc=0, column='timestamp', value = timestamp)
    try:
        push_panda_table_sql(connection, table_name, df)
    except:
        print["Connection down, SQL not sent"]
        
    if verbose: print("[SQL sent]")
    #df.to_sql("Run10000", con=connection, if_exists='append', index_label='id')
    
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
    
def checkNewRuns(run_number_start,hv_state):
    
    list_runs_to_analyze = []
    while len(list_runs_to_analyze) == 0:
        df = cy.read_cygno_logbook(verbose=False)
        list_runs_to_analyze = df.run_number[(df["storage_cloud_status"] == 1) & (df["online_reco_status"] == -1) & (df["run_number"] > run_number_start) & (df["HV_STATE"] == hv_state)].values.tolist()
        time.sleep(5)

    return list_runs_to_analyze

def sql_update_reco_status(run,value,connection):
    cmd.update_sql_value(connection, table_name="Runlog", row_element="run_number", 
                     row_element_condition=run, 
                     colum_element="online_reco_status", value=value, 
                     verbose=True)
    

def get_put_2cloud(fun, localpath, key, url, bucket, session, verbose):
    
    import boto3
    import requests
    from boto3sts import credentials as creds
    import urllib.parse

    session = creds.assumed_session(session, endpoint=url,verify=True)
    s3 = session.client('s3', endpoint_url=url, config=boto3.session.Config(signature_version='s3v4'), verify=True)
    if fun == "get":
        url_out = s3.generate_presigned_url('get_object', 
                                        Params={'Bucket': bucket,
                                                'Key': key}, 
                                        ExpiresIn=3600)
    elif fun == "put":
        url_out = s3.generate_presigned_post(bucket, key, ExpiresIn=3600)
        with open(localpath, 'rb') as f:
            files = {'file': (localpath, f)}
            http_response = requests.post(url_out['url'], data=url_out['fields'], files=files)
    else:
        url_out = ''
    
    return url_out
        

def writeped2root(pedrun, pedmean, pedrms, option='update', verbose=False):
    import ROOT
    
    pedfilename = "pedestals/pedmap_run%s_rebin1.root" % (pedrun)
    (nx,ny) = pedmean.shape
    #h2 = ROOT.TH2D('pic_run',fname+'_'+str(id),nx,0,nx,ny,0,ny)
    
    pedfile = ROOT.TFile.Open(pedfilename,'recreate')
    pedmap = ROOT.TH2D('pedmap','pedmap',nx,0,nx,ny,0,ny)
    pedmapS = ROOT.TH2D('pedmapsigma','pedmapsigma',nx,0,nx,ny,0,ny)
    
   
    # now save in a persistent ROOT object
    for ix in range(nx):
        for iy in range(ny):
            pedmap.SetBinContent(ix+1,iy+1,pedmean[ix,iy]);
            pedmap.SetBinError(ix+1,iy+1,pedrms[ix,iy]);
            pedmapS.SetBinContent(ix+1,iy+1,pedrms[ix,iy]);

    pedfile.cd()
    pedmap.Write()
    pedmapS.Write()
    pedmean1D = ROOT.TH1D('pedmean','pedestal mean',500,97,103)
    pedrms1D = ROOT.TH1D('pedrms','pedestal RMS',1000,0,10)
    for ix in range(nx):
        for iy in range(ny):
            pedmean1D.Fill(pedmap.GetBinContent(ix,iy)) 
            pedrms1D.Fill(pedmap.GetBinError(ix,iy)) 
    pedmean1D.Write()
    pedrms1D.Write()
    pedfile.Close()
    
    if verbose:
        print("Pedestal calculated and saved into ",pedfilename)
        
    return pedfilename

def main(run_number_start, hv_state, verbose=True):
    
    #client = midas.client.MidasClient("middleware")
    #buffer_handle = client.open_event_buffer("SYSTEM",None,1000000000)
    #request_id = client.register_event_request(buffer_handle)
    
    # init program variables
    t0 = time.time()
    nsigma        = 1.3
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
    #header_environment = client.odb_get("/Equipment/Environment/Settings/Names Input")
    #header_environment = header_event + header_environment

    # DEBUG VARABLE
    
    t1bc = time.time()
    
    while True:
        t0bc = time.time()
        
        list_runs_to_analyze = checkNewRuns(run_number_start, hv_state)
        print("Getting List of runs")
        
        run_number = list_runs_to_analyze[0]
        sql_update_reco_status(run_number,0,connection)
        
        dfrun = cy.run_info_logbook(run=run_number, sql=True, verbose=False)
        mfile = cy.open_mid(run=run_number, path='/jupyter-workspace/cloud-storage/cygno-data/', cloud=True, tag='LNGS', verbose=True)
        
        print("Starting analysing the first one")
        

        #event = client.receive_event(buffer_handle, async_flag=True)

        #state         = client.odb_get("/Runinfo/State")
        #gem_hv_state  = client.odb_get("/Equipment/HV/Variables/ChState[0]")
        exposure_time = dfrun["exposure_sec"].values[0]
        
        for event in mfile:
            t0b = time.time()
            if event.header.is_midas_internal_event():
                print("Saw a special event")
                continue
        
        #if event is not None:
        #    t0b = time.time()
        #    if event.header.is_midas_internal_event():
        #        if verbose:
        #            print("Saw a special event")
        #        continue

            # global event useful variables
            bank_names    = ", ".join(b.name for b in event.banks.values())
            event_info    = [event.header.timestamp, event.header.serial_number, event.header.event_id]
            #free_running  = client.odb_get("/Configurations/FreeRunning")
            #run_number    = client.odb_get("/Runinfo/Run number")
            event_number  = event.header.serial_number
            event_time    = datetime.fromtimestamp(event.header.timestamp).strftime('%Y-%m-%d %H:%M:%S')

            if verbose:
                print("Event # %s of type ID %s contains banks %s" % (event.header.serial_number, event.header.event_id, bank_names))
                print("Received event with timestamp %s containing banks %s" % (event.header.timestamp, bank_names))
                print("%s, banks %s" % (datetime.utcfromtimestamp(event.header.timestamp).strftime('%Y-%m-%d %H:%M:%S'), bank_names))


                
            for bank_name, bank in event.banks.items():
                start = time.perf_counter()
                t1bc = time.time()
                if bank_name=='CAM0': # CAM image
                    image, shape_image, _ = cy.daq_cam2array(bank)
                    if init_cam:
                        m_image = np.zeros((shape_image, shape_image), dtype=np.float64)
                        s_image = np.zeros((shape_image, shape_image), dtype=np.float64)
                        if verbose: print("image shape: "+str(shape_image)) 
                        init_cam = False
                    #if event is not None:
                     
                    t1 = time.time()


                    ## Skipping spark images
                    if skipSpark(image):
                        continue

                    if dfrun["HV_STATE"].values[0] == 0:
                        if verbose: print("[Storing ped data {:d} images]".format(ped_id))
                        #ped_array.append(image)
                        
                        recoPedAndUpdate(image, run_number, event_number, event.header.timestamp, connection, verbose)

                        m_image += image
                        s_image += image**2

                        exposure_ped = exposure_time
                        ped_id+= 1

                    elif dfrun["HV_STATE"].values[0] == 1:
                        if verbose: print("[Initiating Reconstruction]")
                        if not len(pedarr_fr):
                            if verbose: print("[Loading Pedestal]")
                            
                            dfped  = dfrun[(dfrun.online_reco_status == 1) & (dfrun.HV_STATE == 0) & (dfrun.run_number < run_number)]
                            pedrun = dfped.sort_values(by='run_number', ascending=False).run_number.values[0]
                            pedfilename_get = 'pedmap_run%s_rebin1.root' % (pedrun)
                            
                            url_ped   = get_put_2cloud('get', '', 'middleware/'+pedfilename_get, URL, 'cygno-analysis', 'dodas', verbose=verbose)
                            
                            pedrf_fr  = uproot.open(url_ped)
                            pedarr_fr = pedrf_fr['pedmap'].values().T
                            sigarr_fr = pedrf_fr['pedmap'].errors().T
                            
                            #pedarr_fr = np.load(DEFAULT_PATH_ONLINE+"pedarr_%.1f.npy" % exposure_time)
                            #sigarr_fr = np.load(DEFAULT_PATH_ONLINE+"sigarr_%.1f.npy" % exposure_time)
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
                        #reconstruction_sample_gap = client.odb_get("/middleware/reconstruction_sample_gap")    
                        #if (event_number%reconstruction_sample_gap) == 0:
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

                t3b = time.time()
                end = time.perf_counter()
                print("Run: {:d} Event: {:d} at {:s}".format(run_number, event_number, event_time))
                print("Elapsed, slow {:.2f}, pmt {:.2f}, cam {:.2f}, read cam {:.2f}, subprocess {:.2f} ".format(t3b-t2b, t2b-t1b, t1b-t0b, t1bc-t0bc, end-start) )
            #save_ped = client.odb_get("/middleware/save_ped")
        ## End of the run
        sql_update_reco_status(run_number,1,connection)
        ## remove file from tmp
        os.remove('/tmp/run%05d.mid.gz' % run_number)
        if (ped_id > 0):
            print("[Making Pedestal over {:d} images]".format(ped_id))
            #pedarr_fr, sigarr_fr = makeped(ped_array)
            pedarr_fr = m_image/ped_id
        
            sigarr_fr = np.sqrt((s_image - pedarr_fr**2 * ped_id) / (ped_id - 1))
            #m_image[np.isnan(s_image)==True]=m_image.mean() # pach per i valori insani di sigma e media
            #s_image[np.isnan(s_image)==True]=1024
            np.save(DEFAULT_PATH_ONLINE+"pedarr_%.1f.npy" % exposure_ped, pedarr_fr)
            np.save(DEFAULT_PATH_ONLINE+"sigarr_%.1f.npy" % exposure_ped, sigarr_fr)
            #pedmap_run4155_rebin1.root
            
            # Save pedmap into ROOT file
            writeped2root(run_number, pedarr_fr, sigarr_fr, option='update', verbose=True)
            pedfilename = 'pedmap_run%s_rebin1.root' % (run_number)
            # Upload the file into the CLOUD
            get_put_2cloud('put', DEFAULT_PATH_ONLINE+pedfilename, 'middleware/'+pedfilename, URL, 'cygno-analysis', 'dodas', verbose=verbose)
            
            os.remove(DEFAULT_PATH_ONLINE+pedfilename)
            ped_id = 0
            m_image = np.zeros((shape_image, shape_image), dtype=np.float64)
            s_image = np.zeros((shape_image, shape_image), dtype=np.float64)
            #client.odb_set("/middleware/save_ped", False)
            if verbose: print("[Pedestal done]")
        #client.communicate(10)
        #time.sleep(0.1)
        

    #client.deregister_event_request(buffer_handle, request_id)

    #client.disconnect()
    
        
if __name__ == "__main__":
    from optparse import OptionParser
    parser = OptionParser(usage='usage: %prog\t [-ubsv] run_number_start hv_state')
    parser.add_option('-v','--verbose', dest='verbose', action="store_true", default=False, help='verbose output;');
    (options, args) = parser.parse_args()
    #main(verbose=options.verbose)
    
    if len(args) < 2:
        print(args, len(args))
        parser.error("incorrect number of arguments")

    else:
        main(int(args[0]), int(args[1]), options.verbose)
