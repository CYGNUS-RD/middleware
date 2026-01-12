#!/usr/bin/env python3
#
# I. Abritta and G. Mazzitelli May 2023
# Middelware online recostruction 
# Modify by ... in date ...
#

#from matplotlib import pyplot as plt
import numpy as np
import os
import os.path
import stat
#from datetime import datetime
import datetime
import time
import pandas as pd
import subprocess
import re
import json

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
PATH_DEV            = '/root/dev/'

def getSQLrun(run,verbose=False):
    
    df = []
    while len(df) == 0:
        try:
            df = cy.run_info_logbook(run=run, sql=True, verbose=verbose)
        except:
            print("Error connecting to SQL, trying again in 30s", end='\r')
            df = []
            time.sleep(10)

    return df

    
def checkNewRuns(run_number_start, run_number_end):
    
    list_runs_to_analyze = []
    #while len(list_runs_to_analyze) == 0:
    try:
        #df = cy.read_cygno_logbook(verbose=False)
        df = cy.read_cygno_logbook(tag="LNGS",start_run=run_number_start,end_run=run_number_end+1)
        print("DB connected")
    except:
        print("Error connecting to SQL, trying again in 30s")
        df = pd.DataFrame()
        list_runs_to_analyze = []
        time.sleep(10)
    if not df.empty:
        list_runs_to_analyze = df.run_number[(df["number_of_events"] > 10) & (df["storage_cloud_status"] == 1) & (df["online_reco_status"] == -1) & (df["run_number"] >= run_number_start) & (df["run_number"] <= run_number_end)].values.tolist()

        if len(list_runs_to_analyze) == 0:
            print("Waiting 10 seconds to check new files again")
            time.sleep(10)
        else:
            print("New files to be reconstructed found")
    else:
        list_runs_to_analyze = []
            
    return list_runs_to_analyze

def sql_update_reco_status(run,value,connection):
    status = cmd.update_sql_value(connection, table_name="Runlog", row_element="run_number", 
                     row_element_condition=run, 
                     colum_element="online_reco_status", value=value, 
                     verbose=True)
    return status    
    

def checkCondorStatus():
    process = subprocess.Popen(
        ['condor_q', '-all', '-format', '%-12s', 'Owner', '-format', '%-3s', 'JobStatus', '-format', '%10s', 'QDate', '-format', '%4s', 'ClusterId', '-format', '%3s.', 'ProcId', '-format', '%-8s', 'JobArgs', '-format', '%-15s', 'JobStartDate', '-format', '%-20s\n', 'Cmd'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    output, error = process.communicate()
    
    print(output)

    if error:
        raise Exception(f"Error in executing condor_q: {error}")

    output = output.decode('utf-8')

    header = ["Owner", "JobStatus", "QDate", "ClusterId", "ProcId", "JobStartDate", "JobArgs"]

    df = pd.DataFrame([x.split() for x in output.split('\n')[1:-1]], columns=header)

    # convert JobStatus to readable string
    df['JobStatus'] = df['JobStatus'].map({'0': 'Unexpanded', '1': 'Idle', '2': 'Running', '3': 'Removed', '4': 'Completed', '5': 'Held', '6': 'Transferring Output', '7': 'Suspended'})

    # convert QDate to datetime format
    df['QDate'] = pd.to_datetime(df['QDate'], unit='s').dt.strftime('%m/%d %H:%M')

    # convert JobStartDate to datetime format
    df['JobStartDate'] = pd.to_datetime(df['JobStartDate'], unit='s').dt.strftime('%m/%d %H:%M')

    return df

def sendjob(PATH_DEV, submit_run, autoreconame): 
    print(subprocess.check_output(f"pwd", shell=True))
    try:
        output = subprocess.check_output(f"source {PATH_DEV}subber.sh {submit_run} {autoreconame} && echo $ClusterID", shell=True)
        cluster_id_string = output.decode("utf-8").strip()
        cluster_id = int(cluster_id_string.split(" ")[-1].split(".")[0])
        print(f"Job submitted successfully with ClusterID {cluster_id}")
    except:
        print("Job submission failed.")
        cluster_id = 0
    
    return cluster_id

def idleJobsCount(idlejobs_old):
    # Run the condor_q -totals command
    command = "condor_q -totals"
    try:
        output   = subprocess.check_output(command, shell=True)
        idlejobs_new = int(((((str(output).split('\\n'))[4]).split(", "))[2].split())[0])
    except subprocess.CalledProcessError as e:
        print(f"Error running the command: {e}")
        idlejobs_new = idlejobs_old

    return idlejobs_new

def getJobStatus(cluster_id):
    
    for i in range(3):
        try:
            process = subprocess.Popen(
                ['condor_q', str(cluster_id)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

            output, error = process.communicate()

            if error:
                raise Exception(f"Error in executing condor_q: {error}")
            break
        except:
            print("Token error, retrying %d.." %i)

    status = "unknown"
    output = output.decode('utf-8')
    # Extract the relevant line containing the job status
    status_line = re.findall(r"Total for query: 1 jobs; .*\n", output)

    if status_line:
        # Extract the status from the line
        status_match = re.search(r"\d completed, \d removed, \d idle, \d running, \d held, \d suspended", status_line[0])
        if status_match:
            status_str = status_match.group(0)
            completed, removed, idle, running, held, suspended = map(int, re.findall(r"\d+", status_str))
            if completed > 0:
                status = "completed"
            elif running > 0:
                status = "running"
            elif idle > 0:
                status = "idle"
            elif held > 0:
                status = 'held'
            elif suspended > 0:
                status = 'suspended'

    return status

def update_job_status(df, cluster_id, status):
    """
    Update job status DataFrame with the given cluster_id and status.
    If the cluster_id already exists, update the status column, otherwise add a new row to the DataFrame.

    Args:
    df: pandas.DataFrame
        DataFrame containing job status information.
    cluster_id: str
        Cluster ID of the job.
    status: str
        Status of the job.

    Returns:
    pandas.DataFrame
        Updated DataFrame with job status information.
    """

    # check if cluster_id already exists in the DataFrame
    if cluster_id in df['Cluster_ID'].values:
        df.loc[df['Cluster_ID'] == cluster_id, 'Status'] = status
    else:
        # add new row with default values
        #df = df.append({'Cluster_ID': cluster_id, 'Run_number': 0, 'Status': status, 'Data_transfered': 0, 'Cloud_storage': 0, 'JobInQueue': 0}, ignore_index=True)
        df.loc[len(df)] = {'Cluster_ID': cluster_id, 'Run_number': 0, 'Status': status, 'Data_transfered': 0, 'Cloud_storage': 0, 'JobInQueue': 0}
    
    return df

def condorTransferData(cluster_id, df):
    try:
        process = subprocess.Popen(
            ['condor_transfer_data', str(cluster_id)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        output, error = process.communicate()
        if error:
            raise Exception(f"Error in executing condor_transfer_data: {error}")
        else:
            print("Job %s transfered to Sentinel machine" %cluster_id)
            #Update Data_transfered column
            df.loc[df['Cluster_ID'] == cluster_id, 'Data_transfered'] = 1
    except Exception as error2:
        raise Exception(f"Error in executing condor_transfer_data: {error2}")

    return df
        

def forOverPandasStatus(df):# Define the two filters
    filter1 = df['Status'] != 'completed'

    # Loop over the rows of the DataFrame and apply the filters
    for index, row in df.iterrows():
        if filter1[index]:
            #Check Status
            status = getJobStatus(row['Cluster_ID'])
            #Update dataFrame
            df = update_job_status(df, row['Cluster_ID'], status)
    return df

def forOverPandasTransfer(df):# Define the two filters
    filter1 = df['Status'] == 'completed'
    filter2 = df['Data_transfered'] == 0

    # Loop over the rows of the DataFrame and apply the filters
    for index, row in df.iterrows():
        if filter1[index] and filter2[index]:
            cluster_ID_row = row['Cluster_ID']
            #Run condor_transfer_data and #Update dataFrame
            df = condorTransferData(cluster_ID_row, df)
            #sql_update_reco_status(row['Run_number'],1,connection) #Update the online_reco variable to 1, which means "reconstructed"
    
    return df

def statusReco(path):
    """
    Reads a status file with three lines like:

    Main program return: 0
    copy file reco_run60000_3D.root: 0
    copy file reco_run60000_3D.txt: 0

    Returns:
        reco_status (bool)
        upload_status (bool)
    """
    with open(path, "r") as f:
        lines = f.readlines()

    # Extract numeric values from each line
    # Split by ':' and strip spaces
    try:
        val_main  = int(lines[0].split(":")[1].strip())
        val_root  = int(lines[1].split(":")[1].strip())
        val_text  = int(lines[2].split(":")[1].strip())
    except Exception as e:
        raise ValueError("File format is invalid") from e

    reco_status = (val_main == 0)
    upload_status = (val_root == 0 and val_text == 0)

    return reco_status, upload_status


def forOverPandasCloud(df,connection):# Define the two filters
    filter1 = df['Status'] == 'completed'
    filter2 = df['Data_transfered'] == 1
    filter3 = df['Cloud_storage'] == 0
    

    # Loop over the rows of the DataFrame and apply the filters
    for index, row in df.iterrows():
        if filter1[index] and filter2[index] and filter3[index]:
            cluster_ID_row = row['Cluster_ID']
            run_number_row = row['Run_number']
            #Run data2cloud
            #recofilename = '%s_run%05d_%s.root' % ('reco', run_number_row, '3D')
            recofilename = '%s%05d.log' % ('return_autoreco', run_number_row)
            recofolder   =  '/tmp/' 
            returnpath   = recofolder + recofilename
            
            recoStatus, uploadStatus = statusReco(recofolder + recofilename)
            
            if recoStatus and uploadStatus:
                sql_update_reco_status(row['Run_number'],1,connection) #Update the online_reco variable to 1, which means "reconstructed"
                #Update dataFrame
                df.loc[df['Cluster_ID'] == cluster_ID_row, 'Cloud_storage'] = 1
            else:
                df.loc[df['Cluster_ID'] == cluster_ID_row, 'Status'] = 'held'
                
    return df

def forOverPandasCloud_rm(df):# Define the two filters
    filter1 = df['Status'] == 'completed'
    filter2 = df['Data_transfered'] == 1
    filter3 = df['Cloud_storage'] == 1
    filter4 = df['JobInQueue'] == 0
    

    # Loop over the rows of the DataFrame and apply the filters
    for index, row in df.iterrows():
        if filter1[index] and filter2[index] and filter3[index] and filter4[index]:
            cluster_ID_row = row['Cluster_ID']
            print("Removing Job %s from the condor queue" %cluster_ID_row)
            try:
                process = subprocess.Popen(
                    ['condor_rm', str(cluster_ID_row)],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                output, error = process.communicate()

                print(output)

                if error:
                    raise Exception(f"Error in executing condor_rm: {error}")
                df.loc[df['Cluster_ID'] == cluster_ID_row, 'JobInQueue'] = 1
            except:
                print("Retry")
    return df

def forOverPandasHeld(df, connection):# Define the two filters
    filter1 = df['Status'] == 'held'
#    filter2 = df['Data_transfered'] == 0
    filter3 = df['Cloud_storage'] == 0   

    # Loop over the rows of the DataFrame and apply the filters
    for index, row in df.iterrows():
        if filter1[index]  and filter3[index]:
            cluster_ID_row = row['Cluster_ID']
            print("Removing Job %s from the condor queue" %cluster_ID_row)
            try:
                process = subprocess.Popen(
                    ['condor_rm', str(cluster_ID_row)],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                output, error = process.communicate()

                print(output)

                if error:
                    raise Exception(f"Error in executing condor_rm: {error}")
                print("Restoring the job to the Queue")
                sql_update_reco_status(row['Run_number'],-1,connection)
                df = df.drop(df.loc[df['Cluster_ID'] == cluster_ID_row].index)                
            except:
                print("Retry")
    return df

def forOverPandasUnknown(df, connection):# Define the two filters
    filter1 = df['Status'] == 'unknown'
    filter2 = df['Data_transfered'] == 0
    filter3 = df['Cloud_storage'] == 0   

    # Loop over the rows of the DataFrame and apply the filters
    for index, row in df.iterrows():
        if filter1[index] and filter2[index] and filter3[index]:
            cluster_ID_row = row['Cluster_ID']
            print("Removing Job %s from the condor queue" %cluster_ID_row)
            try:
                print("Restoring the job to the Queue")
                sql_update_reco_status(row['Run_number'],-1,connection)
                df = df.drop(df.loc[df['Cluster_ID'] == cluster_ID_row].index)                
            except:
                print("Retry")
    return df


def refreshSQL(verbose=False):
    if verbose:
        print("Setting SQL environment")

    print(os.environ['MYSQL_IP'])
    print("-----------")
    
    # init sql variabile and connector
    connection = mysql.connector.connect(
      host     = os.environ['MYSQL_IP'],
      user     = os.environ['MYSQL_USER'],
      password = os.environ['MYSQL_PASSWORD'],
      database = os.environ['MYSQL_DATABASE'],
      port     = int(os.environ['MYSQL_PORT'])
    )
    
    return connection    

def create_json_with_date_time(outname):
    
    # Get the current date and time
    current_date_time = datetime.datetime.now()

    # Add two hours to the current date and time
    new_date_time = current_date_time #+ datetime.timedelta(hours=1)

    # Create a dictionary containing the modified date and time information
    data = {
        'last_update': new_date_time.strftime('%Y-%m-%d %H:%M:%S')
    }

    # Write the dictionary to a JSON file
    with open('/root/dev/lu_'+ outname +'.json', 'w') as json_file:
        json.dump(data, json_file, indent=4)
        
def savetables(df_condor, outname):
    df_condor.to_csv('/root/submitJobs/'+ outname +'.csv', index=False)
    df_condor.to_csv('/root/dev/'+ outname +'.csv', index=False)
    df_condor.to_json('/root/dev/'+ outname +'.json', orient="table")
    create_json_with_date_time(outname)
    
    
def main(run_number_start, run_number_end, nproc, maxidle, TAG, recopath = 'reconstruction', outname = 'df_condor', just_status = False, verbose = False):
    #Set environment variables
    connection = refreshSQL(verbose)
    outname    = options.outname

    submit_path      = "/root/submitJobs/"
    file_path = submit_path + outname + '.csv'

    if os.path.isfile(file_path):
        df_condor = pd.read_csv(file_path)
        if verbose:
            print("File loaded successfully!\n", end='\r')
    else:
        if verbose:
            print("Creating new DataFrame \n", end='\r')
        # create an empty DataFrame with the desired columns
        columns_condor = ['Cluster_ID', 'Run_number', 'Status', 'Data_transfered', 'Cloud_storage', 'JobInQueue']
        df_condor = pd.DataFrame(columns=columns_condor)
        
    savetables(df_condor, outname)

    maxentries       = -1

    # set the initial time
    start_time    = time.time()
    aux_rm        = 0
    aux_held      = 0
    idlejobs      = 0
    #maxidle       = 30
    

    while True:
    #for i in range(5):
        
        # check if 2 minutes have passed
        elapsed_time = time.time() - start_time
        if elapsed_time >= 3000:
            connection = refreshSQL(verbose)
            # reset the start time
            start_time = time.time()
        
        ##Check if the run arrived at the cloud 
        list_runs_to_analyze = checkNewRuns(run_number_start,run_number_end)
        
        ### Routine to not let the over sent jobs
        idlejobs = idleJobsCount(idlejobs)
        if verbose:
            print("Number of Jobs in Idle: " + str(idlejobs) + "\n", end='\r')
        
        if idlejobs > maxidle:
            if verbose:
                print("Idle Jobs limit reached \n", end='\r')
            idle_status = True
        else:
            if verbose:
                print("Sentinel can still accept more jobs \n", end='\r')
            idle_status = False
            
        if just_status == False:
            if idle_status == False:
                while (len(list_runs_to_analyze) > 0) and (idlejobs <= maxidle): ## keep send jobs to condor if we have new runs to analyze
                    submit_run = list_runs_to_analyze[-1] # Get the first run to go to the queue
                    autoreconame = "autoreco"+str(submit_run)
                    status = sql_update_reco_status(submit_run,-2,connection) #"idle"
    
                    if verbose:
                        print("Sending the Run "+ str(submit_run) + " to the Queue \n", end='\r')
    
                    cluster_id = sendjob(PATH_DEV,submit_run,autoreconame)
                    if cluster_id:
                        df_condor  = update_job_status(df_condor, cluster_id, "idle")
                        status = sql_update_reco_status(submit_run,0,connection) #Update the online_reco variable to 0, which means "reconstructing"
                        if verbose:
                            print("Update Table: %d" %status, end='\r')
                        if status == -2:
                            connection = refreshSQL(verbose)
                            status = sql_update_reco_status(submit_run,0,connection) #Update the online_reco variable to 0, which means "reconstructing"
    
                        if verbose:
                            print("Run " + str(submit_run)+ "submitted with Cluster_ID: " + str(cluster_id) + "\n", end='\r')
    
                        jobStatus  = getJobStatus(cluster_id)
                        df_condor  = update_job_status(df_condor, cluster_id, jobStatus)
                        # Insert run_number information to the dataframe
                        df_condor.loc[df_condor['Cluster_ID'] == cluster_id, 'Run_number'] = submit_run           
    
                        if verbose:
                            print("Saving Condor DataFrame Control Monitor", end='\r')
                            print("\n")
                            print(df_condor, end='\r')
                            print("\n")
                        #df_condor.to_csv('../submitJobs/'+ outname +'.csv', index=False)
                        #df_condor.to_json('../dev/'+ outname +'.json', orient="table")
                        savetables(df_condor, outname)
                        
                        ### Routine to not let autoreco over sent jobs
                        idlejobs = idleJobsCount(idlejobs)
                        if verbose:
                            print("Number of Jobs in Idle: " + str(idlejobs) + "\n", end='\r')
    
                    #Checking again the list to see if there is more Run to be analyzed
                    df_condor = forOverPandasStatus(df_condor)
                    df_condor = forOverPandasTransfer(df_condor)
                    df_condor = forOverPandasCloud(df_condor, connection)
                    df_condor = forOverPandasCloud_rm(df_condor)
                    list_runs_to_analyze = checkNewRuns(run_number_start,run_number_end)
        else:
            if verbose:
                print("Sentinel in Drain, just checking status\n", end='\r')
                

        
        
        df_condor = forOverPandasStatus(df_condor)
        df_condor = forOverPandasTransfer(df_condor)
        df_condor = forOverPandasCloud(df_condor, connection)
        #df_condor.to_csv('../submitJobs/'+ outname +'.csv', index=False)
        #df_condor.to_json('../dev/'+ outname +'.json', orient="table")
        savetables(df_condor, outname)
        
        
        nheld = 15
        if aux_held >= nheld:
            if verbose:
                print("Checking completed Jobs on Queue\n", end='\r')
            connection = refreshSQL(verbose)
            # reset the start time
            df_condor = forOverPandasCloud_rm(df_condor)
            df_condor = forOverPandasHeld(df_condor, connection)
            savetables(df_condor, outname)
            aux_held = 0
        else:
            if verbose:
                print("Next check of Queue in %d loops\n" %(nheld-aux_held), end='\r')
        
        
        #elapsed_time_rm = time.time() - start_time_rm
        nfresh = 20
        if aux_rm >= nfresh:
            if verbose:
                print("Killing agent and refreshing token\n", end='\r')
            time.sleep(40)
            connection = refreshSQL(verbose)
            # reset the start time
            aux_rm = 0
        else:
            if verbose:
                print("Next cleaning in %d loops\n" %(nfresh-aux_rm), end='\r')
        #df_condor = forOverPandasUnknown(df_condor, connection)
        
        if verbose:
            print("\n")
            print(df_condor, end='\r')
            print("\n")
            print("Saving Condor DataFrame Control Monitor\n", end='\r')
        # save the dataframe to a CSV file
        savetables(df_condor, outname)
        #df_condor.to_csv('../submitJobs/'+ outname +'.csv', index=False)
        #df_condor.to_json('../dev/'+ outname +'.json', orient="table")
        if verbose:
            print("Waiting 60 seconds to check Job status\n", end='\r')
        aux_rm = aux_rm + 1
        aux_held = aux_held + 1
        time.sleep(5)


if __name__ == "__main__":
    from optparse import OptionParser
    parser = OptionParser(usage='usage: %prog\t [-ubsv] run_number_start')
    parser.add_option('-e', '--run-end', dest='run_number_end', default=99999, type=int, help='last run number to be analyzed')
    parser.add_option('-j', '--nproc', dest='nproc', default=3, type=int, help='number of cores to use')
    parser.add_option('-i', '--maxidle', dest='maxidle', default=30, type=int, help='max number of jobs in idle')
    parser.add_option('-t', '--tag', dest='TAG', default=None, type='string', help='TAG where to save the output reco')
    parser.add_option('-f', '--recopath', dest='recopath', default='reconstruction', type='string', help='Name of the reconstruction folder')
    parser.add_option('-o', '--outname', dest='outname', default='df_condor', type='string', help='prefix for the output file name')
    parser.add_option('-s','--just-status', dest='just_status', default=0, type=int, help='just update status, do not send jobs;')
    parser.add_option('-v','--verbose', dest='verbose', action="store_true", default=False, help='verbose output;');
    (options, args) = parser.parse_args()
    #main(verbose=options.verbose)

    if options.just_status == 1:
        options.just_status = True
    else:
        options.just_status = False
    
    if len(args) < 1:
        print(args, len(args))
        parser.error("incorrect number of arguments")

    else:
        main(int(args[0]), options.run_number_end, options.nproc, options.maxidle, options.TAG, options.recopath, options.outname, options.just_status, options.verbose)

        ## Example:
        # ./fullRecoSentinel_v1.02.py 17182 -o df_condor_coda1 -s 0 -v
