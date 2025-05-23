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

def writeSubmitFile(submit_path, submit_run, nproc, maxentries):
    
    files = getReconstructionList()
    
    with open(submit_path + "submit_" + submit_run, "w") as f:
        f.write("universe   = vanilla\n")
        f.write("executable = /root/reconstruction/exec_reco.sh\n")
        f.write("\n")
        f.write("log    = reconstruction_"+submit_run+".log\n")
        f.write("output = reconstruction_"+submit_run+".out\n")
        f.write("error  = reconstruction_"+submit_run+".error\n")
        f.write("\n")
        f.write("should_transfer_files   = YES\n")
        f.write("when_to_transfer_output = ON_EXIT_OR_EVICT\n")
        f.write("\n")
        f.write("transfer_input_files  = "+ files +"\n\n")
        f.write("transfer_output_files = reco_run"+submit_run+"_3D.root\n")
        f.write("\n")
        f.write("arguments             = configFile_LNGS.txt "+submit_run+" "+ nproc +" "+ maxentries +"\n")
        f.write("\n")
        f.write("+OWNER = \"condor\"\n")
        f.write("queue\n")

        
def createCondorSubmit(submit_path,submit_run):
    submitfile = "submitjobs_" + submit_run + ".sh"
    with open(submit_path + submitfile, "w") as f:
        f.write("condor_submit -spool submit_"+submit_run+"\n")
    
    return submitfile

        
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


def getSQLrun(run,verbose=False):
    
    df = []
    while len(df) == 0:
        try:
            df = cy.run_info_logbook(run=run, sql=True, verbose=verbose)
        except:
            print("Error connecting to SQL, trying again in 30s")
            df = []
            time.sleep(30)

    return df

    
def checkNewRuns(run_number_start):
    
    list_runs_to_analyze = []
    #while len(list_runs_to_analyze) == 0:
    try:
        df = cy.read_cygno_logbook(verbose=False)
        print("DB connected")
    except:
        print("Error connecting to SQL, trying again in 30s")
        df = pd.DataFrame()
        list_runs_to_analyze = []
        time.sleep(30)
    if not df.empty:
        list_runs_to_analyze = df.run_number[(df["number_of_events"] > 1) & (df["storage_cloud_status"] == 1) & (df["online_reco_status"] == -1) & (df["run_number"] > run_number_start) & (df["run_number"] < 28000)].values.tolist()

        if len(list_runs_to_analyze) == 0:
            print("Waiting 90 seconds to check new files again")
            time.sleep(90)
        else:
            print("New files to be reconstruced found")
    else:
        list_runs_to_analyze = []
            
    return list_runs_to_analyze

def getReconstructionList():

    folder_path = "../reconstruction/"
    folder_to_exclude = ".git"

    # Get list of all files and folders in folder
    all_items = os.listdir(folder_path)

    # Filter out the folder to exclude
    items_to_process = [os.path.join(folder_path, item) for item in all_items if not os.path.isdir(os.path.join(folder_path, item)) or item != folder_to_exclude]

    # Convert the list of items into a single string
    items_string = ", ".join(items_to_process)

    # Print the string of items to process
    return items_string

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

def sendjob_2(path,submitfile):

    #submit_script_path = path+submitfile
    print("Changing dir to: " + path)
    os.chdir(path)
    
    print(os.system("ls"))    
    submit_file_path = os.path.abspath(submitfile)
    
    print("Submit file path: ", submit_file_path)
    
    return_code = os.system(f"source {submit_file_path}")

    if return_code == 0:
        print("Command executed successfully")
    else:
        print("Command failed with return code", return_code)
    
    return return_code

def sendjob(path, submitfile):
    refreshToken()
    os.chdir(path)
    fullpath = path+submitfile
    try:
        output = subprocess.check_output(f"source {fullpath} && echo $ClusterID", shell=True)
        cluster_id_string = output.decode("utf-8").strip()
        cluster_id = int(cluster_id_string.split(" ")[-1].split(".")[0])
        print(f"Job submitted successfully with ClusterID {cluster_id}")
    except:
        print("Job submission failed.")
        cluster_id = 0
    
    return cluster_id

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
            refreshToken()

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
        df = df.append({'Cluster_ID': cluster_id, 'Run_number': 0, 'Status': status, 'Data_transfered': 0, 'Cloud_storage': 0, 'JobInQueue': 0}, ignore_index=True)
    
    return df

def condorTransferData(cluster_id, df):
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

def forOverPandasTransfer(df, connection):# Define the two filters
    filter1 = df['Status'] == 'completed'
    filter2 = df['Data_transfered'] == 0

    # Loop over the rows of the DataFrame and apply the filters
    for index, row in df.iterrows():
        if filter1[index] and filter2[index]:
            cluster_ID_row = row['Cluster_ID']
            #Run condor_transfer_data and #Update dataFrame
            df = condorTransferData(cluster_ID_row, df)
            sql_update_reco_status(row['Run_number'],1,connection) #Update the online_reco variable to 1, which means "reconstructed"
    
    return df

def forOverPandasCloud(df):# Define the two filters
    filter1 = df['Status'] == 'completed'
    filter2 = df['Data_transfered'] == 1
    filter3 = df['Cloud_storage'] == 0
    

    # Loop over the rows of the DataFrame and apply the filters
    for index, row in df.iterrows():
        if filter1[index] and filter2[index] and filter3[index]:
            cluster_ID_row = row['Cluster_ID']
            run_number_row = row['Run_number']
            #Run data2cloud
            recofilename = '%s_run%05d_%s.root' % ('reco', run_number_row, '3D')
            recofolder   =  '../submitJobs/' 
            
            uploadStatus = reco2cloud(recofilename, recofolder, run_number_row, verbose=False)
            
            if uploadStatus:          
                #Update dataFrame
                df.loc[df['Cluster_ID'] == cluster_ID_row, 'Cloud_storage'] = 1
                
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
    filter2 = df['Data_transfered'] == 0
    filter3 = df['Cloud_storage'] == 0   

    # Loop over the rows of the DataFrame and apply the filters
    for index, row in df.iterrows():
        if filter1[index] and filter2[index] and filter3[index]:
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

def createPedLog():
    #get the most updated table and create the runlog table
    df = cy.read_cygno_logbook(verbose=False)
    df.to_csv('../reconstruction/pedestals/runlog_LNGS_auto.csv',index=False)
            
def reco2cloud(recofilename, recofolder, run_number, verbose=False):
      #
    # deault parser value
    #
    TAG         = "RECO/Winter23"
    session     = "sentinel-wlcg"
    bucket      = "cygno-analysis"
    max_tries   = 5
    
    INAPATH     = recofolder
    file_in_dir = recofilename
    
    filesize = os.path.getsize(INAPATH+file_in_dir) 
    dtime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    #if verbose:              
    print('{:s} Transferring file: {:s}'.format(dtime, file_in_dir))
    
    current_try = 0
    aux         = 0
    status, isthere = False, False # flag to know if to go to next run
    while(not status):   
        #tries many times for errors of connection or others that may be worth another try
        if verbose: 
            print(INAPATH+file_in_dir,TAG, bucket, session, verbose, filesize)
        status, isthere = cy.s3.obj_put(INAPATH+file_in_dir,tag=TAG, 
                                     bucket=bucket, session=session, 
                                     verbose=verbose)
        if status:
            if isthere:
                remotesize = cy.s3.obj_size(file_in_dir,tag=TAG, 
                                 bucket=bucket, session=session, 
                                 verbose=verbose)

                cy.cmd.rm_file(INAPATH+file_in_dir)
                
                cy.cmd.rm_file(INAPATH + 'reconstruction_' + str(run_number) + '.log')
                cy.cmd.rm_file(INAPATH + 'reconstruction_' + str(run_number) + '.out')
                cy.cmd.rm_file(INAPATH + 'reconstruction_' + str(run_number) + '.error')
                
                if verbose:              
                    print('{:s} file removed: {:s}'.format(dtime, file_in_dir))

                ##############################
                if verbose: 
                    print('{:s} Upload done: {:s}'.format(dtime, file_in_dir))
                aux = 1

        else:
            current_try = current_try+1
            if current_try==max_tries:
                print('{:s} ERROR: Max try number reached: {:d}'.format(dtime, current_try))
                status=True
                aux = 0
    return aux


def refreshSQL(verbose=False):
    if verbose:
        print("Setting SQL environment")
    
    process2 = subprocess.Popen(
        "source ../SQLSetup.sh", shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    output2, error2 = process2.communicate()
    
    # init sql variabile and connector
    connection = mysql.connector.connect(
      host=os.environ['MYSQL_IP'],
      user=os.environ['MYSQL_USER'],
      password=os.environ['MYSQL_PASSWORD'],
      database=os.environ['MYSQL_DATABASE'],
      port=int(os.environ['MYSQL_PORT'])
    )
    
    return connection

def killagent(verbose=False):
    if verbose:
        print("Cleaning oidc-agent")
    
    #killall oidc-agent
    process = subprocess.Popen(
        "killall oidc-agent", shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    output, error = process.communicate()

def refreshToken(verbose=False):
    if verbose:
        print("Setting Condor environment")
    
    #process = subprocess.Popen(
    #    "source ../start_script_2.sh", shell=True,
    #    stdout=subprocess.PIPE,
    #    stderr=subprocess.PIPE
    #)
    
    #output, error = process.communicate()
    
    output = subprocess.check_output("source ../start_script_2.sh", shell=True)
    

def create_json_with_date_time(outname):
    
    # Get the current date and time
    current_date_time = datetime.datetime.now()

    # Add two hours to the current date and time
    new_date_time = current_date_time + datetime.timedelta(hours=2)

    # Create a dictionary containing the modified date and time information
    data = {
        'last_update': new_date_time.strftime('%Y-%m-%d %H:%M:%S')
    }

    # Write the dictionary to a JSON file
    with open('../dev/lu_'+ outname +'.json', 'w') as json_file:
        json.dump(data, json_file, indent=4)
        
def savetables(df_condor, outname):
    df_condor.to_csv('../submitJobs/'+ outname +'.csv', index=False)
    df_condor.to_json('../dev/'+ outname +'.json', orient="table")
    create_json_with_date_time(outname)
    
    
def main(run_number_start, outname='df_condor', just_status=False, verbose=False):
    #Set environment variables
    refreshToken(verbose)
    connection = refreshSQL(verbose)
    outname    = options.outname

    submit_path      = "../submitJobs/"
    file_path = submit_path + outname + '.csv'

    if os.path.isfile(file_path):
        df_condor = pd.read_csv(file_path)
        if verbose:
            print("File loaded successfully!")
    else:
        if verbose:
            print("Creating new DataFrame.")
        # create an empty DataFrame with the desired columns
        columns_condor = ['Cluster_ID', 'Run_number', 'Status', 'Data_transfered', 'Cloud_storage', 'JobInQueue']
        df_condor = pd.DataFrame(columns=columns_condor)
        
    ### to fix some problems
    #for j in range(327,923):
    #df_condor.loc[df_condor['Cluster_ID'] == 5979, 'Cloud_storage'] = 1
    #df_condor.loc[df_condor['Cluster_ID'] == 5980, 'Cloud_storage'] = 1
    #df_condor.loc[df_condor['Cluster_ID'] == 328, 'Cloud_storage'] = 1
    #df_condor.loc[df_condor['Cluster_ID'] == 1893, 'JobInQueue'] = 1
    
    ####Saving Tables
    #df_condor.to_csv('../submitJobs/'+ outname +'.csv', index=False)
    #df_condor.to_json('../dev/'+ outname +'.json', orient="table")    
    savetables(df_condor, outname)

    #run_number_start = 16798
    nproc            = 4
    maxentries       = -1

    # set the initial time
    start_time    = time.time()
    aux_rm        = 0
    aux_held        = 0
    

    while True:
    #for i in range(5):
        
        # check if 2 minutes have passed
        elapsed_time = time.time() - start_time
        if elapsed_time >= 120:
            refreshToken(verbose)
            connection = refreshSQL(verbose)
            # reset the start time
            start_time = time.time()
        
        ##Check if the run arrived at the cloud 
        list_runs_to_analyze = checkNewRuns(run_number_start)
        
        if just_status == False:
        #for i in range(1):
            while len(list_runs_to_analyze) > 0: ## keep send jobs to condor if we have new runs to analyze
                submit_run = list_runs_to_analyze[0] # Get the first run to go to the queue
                status = sql_update_reco_status(submit_run,-2,connection) #"idle"

                if verbose:
                    print("Sending the Run "+ str(submit_run) + " to the Queue")
                createPedLog()
                writeSubmitFile(submit_path, str(submit_run), str(nproc), str(maxentries))
                submitfile = createCondorSubmit(submit_path, str(submit_run))

                cluster_id = sendjob(submit_path,submitfile)
                if cluster_id:
                    status = sql_update_reco_status(submit_run,0,connection) #Update the online_reco variable to 0, which means "reconstructing"
                    if verbose:
                        print("Update Table: %d" %status)
                    if status == -2:
                        connection = refreshSQL(verbose)
                        status = sql_update_reco_status(submit_run,0,connection) #Update the online_reco variable to 0, which means "reconstructing"

                    if verbose:
                        print("Run " + str(submit_run)+ "submitted with Cluster_ID: " + str(cluster_id))

                    status     = getJobStatus(cluster_id)
                    df_condor  = update_job_status(df_condor, cluster_id, status)
                    # Insert run_number information to the dataframe
                    df_condor.loc[df_condor['Cluster_ID'] == cluster_id, 'Run_number'] = submit_run           

                    if verbose:
                        print("Saving Condor DataFrame Control Monitor")
                        print(df_condor)
                    #df_condor.to_csv('../submitJobs/'+ outname +'.csv', index=False)
                    #df_condor.to_json('../dev/'+ outname +'.json', orient="table")
                    savetables(df_condor, outname)

                #Checking again the list to see if there is more Run to be analyzed
                df_condor = forOverPandasStatus(df_condor)
                df_condor = forOverPandasTransfer(df_condor, connection)
                df_condor = forOverPandasCloud(df_condor)
                df_condor = forOverPandasCloud_rm(df_condor)
                list_runs_to_analyze = checkNewRuns(run_number_start)

        
        
        df_condor = forOverPandasStatus(df_condor)
        df_condor = forOverPandasTransfer(df_condor, connection)
        df_condor = forOverPandasCloud(df_condor)
        #df_condor.to_csv('../submitJobs/'+ outname +'.csv', index=False)
        #df_condor.to_json('../dev/'+ outname +'.json', orient="table")
        savetables(df_condor, outname)
        
        
        nheld = 10
        if aux_held >= nheld:
            if verbose:
                print("Checking completed Jobs on Queue")
            refreshToken()
            connection = refreshSQL(verbose)
            # reset the start time
            df_condor = forOverPandasCloud_rm(df_condor)
            df_condor = forOverPandasHeld(df_condor, connection)
            savetables(df_condor, outname)
            aux_held = 0
        else:
            if verbose:
                print("Next check of Queue in %d loops" %(nheld-aux_held))
        
        
        #elapsed_time_rm = time.time() - start_time_rm
        nfresh = 500
        if aux_rm >= nfresh:
            if verbose:
                print("Killing agent and refreshing token")
            #killagent()
            time.sleep(120)
            refreshToken()
            connection = refreshSQL(verbose)
            # reset the start time
            aux_rm = 0
        else:
            if verbose:
                print("Next cleaning in %d loops" %(nfresh-aux_rm))
        #df_condor = forOverPandasUnknown(df_condor, connection)
        
        if verbose:
            print(df_condor)
            print("Saving Condor DataFrame Control Monitor")
        # save the dataframe to a CSV file
        savetables(df_condor, outname)
        #df_condor.to_csv('../submitJobs/'+ outname +'.csv', index=False)
        #df_condor.to_json('../dev/'+ outname +'.json', orient="table")
        if verbose:
            print("Waiting 60 seconds to check Job status")
        aux_rm = aux_rm + 1
        aux_held = aux_held + 1
        time.sleep(60)


if __name__ == "__main__":
    from optparse import OptionParser
    parser = OptionParser(usage='usage: %prog\t [-ubsv] run_number_start')
    parser.add_option('-o', '--outname', dest='outname', default='df_condor', type='string', help='prefix for the output file name')
    parser.add_option('-s','--just-status', dest='just_status', action="store_true", default=False, help='just update status, do not send jobs;')
    parser.add_option('-v','--verbose', dest='verbose', action="store_true", default=False, help='verbose output;');
    (options, args) = parser.parse_args()
    #main(verbose=options.verbose)
    
    if len(args) < 1:
        print(args, len(args))
        parser.error("incorrect number of arguments")

    else:
        main(int(args[0]), options.outname, options.just_status, options.verbose)

        ## Example:
        # ./fullRecoSentinel_v1.02.py 17182 -o df_condor_coda1 -s -v
