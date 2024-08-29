#!/usr/bin/env python3
#
# G. Mazzitelli 2022
# versione DAQ LNGS/LNF per midas file2cloud 
# cheker and sql update Nov 22 
#

def kb2valueformat(val):
    import numpy as np
    if int(val/1024./1024/1024.)>0:
        return val/1024./1024./1024., "Gb"
    if int(val/1024./1024.)>0:
        return val/1024./1024., "Mb"
    if int(val/1024.)>0:
        return val/1024., "Kb"
    return val, "byte"

def download2file(url, fout):
    import requests
    r = requests.get(url)
    size = 0
    with open(fout, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024*1024*10): 
            size = size + len(chunk)
            print(size)
            if chunk: # filter out keep-alive new chunks
                f.write(chunk)
    return 

def get_s3_client(client_id, client_secret, endpoint_url, session_token):
    # Specify the session token, access key, and secret key received from the STS
    import boto3
    sts_client = boto3.client('sts',
            endpoint_url = endpoint_url,
            region_name  = ''
            )

    response_sts = sts_client.assume_role_with_web_identity(
            RoleArn          = "arn:aws:iam:::role/S3AccessIAM200",
            RoleSessionName  = 'cygno',
            DurationSeconds  = 3600,
            WebIdentityToken = session_token # qua ci va il token IAM
            )

    s3 = boto3.client('s3',
            aws_access_key_id     = response_sts['Credentials']['AccessKeyId'],
            aws_secret_access_key = response_sts['Credentials']['SecretAccessKey'],
            aws_session_token     = response_sts['Credentials']['SessionToken'],
            endpoint_url          = endpoint_url,
            region_name           = '')
    return s3


def get_s3_client_rgw():
    # Specify the session token, access key, and secret key received from the STS
    import boto3
    import os

    sts_client = boto3.client('sts', endpoint_url="https://rgw.cloud.infn.it:443", region_name='')


    response = sts_client.assume_role_with_web_identity(
         RoleArn="arn:aws:iam:::role/IAMaccess",
         RoleSessionName='Bob',
         DurationSeconds=3600,
         WebIdentityToken = os.environ['TOKEN'])
 
    s3 = boto3.client('s3',
         aws_access_key_id = response['Credentials']['AccessKeyId'],
         aws_secret_access_key = response['Credentials']['SecretAccessKey'],
         aws_session_token = response['Credentials']['SessionToken'],
         endpoint_url="https://rgw.cloud.infn.it:443")

    return s3

def main(bucket, tag, folder, start_run, end_run, verbose):
    #

    import os
    import sys
    import numpy as np
    import cygno as cy
    import pandas as pd
    import time
    import subprocess

    BASE_URL = 'https://s3.cloud.infn.it/v1/AUTH_2ebf769785574195bde2ff418deac08a/'
#    import mysql.connector

    script_path = os.path.dirname(os.path.realpath(__file__))
    start = end = time.time()

    client_id     = os.environ['IAM_CLIENT_ID']
    client_secret = os.environ['IAM_CLIENT_SECRET']
    mytoken       = os.environ['TOKEN']
    if verbose: print (mytoken)
    if folder == tag:
       key = tag+'/'
    else:
       key = folder
    base_path = BASE_URL+bucket+'/'+key
    if verbose: print(start_run, end_run)
    runInfo=cy.read_cygno_logbook(sql=True, tag=tag, start_run=start_run, end_run=end_run, verbose=verbose)
    if verbose: print(runInfo.tail())
    for i, run in enumerate(runInfo.run_number.values):
        if bucket == 'cygno-data':
           file_in="run{:05d}.mid.gz".format(run)
        if bucket == 'cygno-analysis':
           file_in='reco_run{:5d}_3D.root'.format(run)
        file_url = base_path+file_in
        if (verbose): 
            print("-------------------------")
            print(file_url)
        tmpout = '/tmp/tag_'+file_in
        download2file(file_url, tmpout)
        s3=get_s3_client_rgw()
        s3.upload_file(tmpout, bucket, key+file_in)
        cy.cmd.rm_file(tmpout)

    sys.exit(0)
    
    
if __name__ == "__main__":
    from optparse import OptionParser
    #
    # deault parser value
    #
    TAG         = 'LNF'
    BUCKET      = 'cygno-data'
    SESSION     = 'infncloud-wlcg'


    parser = OptionParser(usage='usage: %prog [-b [{:s}] -t [{:s}] -s[{:s}] -csv]\n'.format(BUCKET,TAG,SESSION))
    parser.add_option('-b','--bucket', dest='bucket', type='string', default=BUCKET, help='PATH to raw data')
    parser.add_option('-t','--tag', dest='tag', type='string', default=TAG, help='tag where dir for data')
    parser.add_option('-f','--folder', dest='folder', type='string', default=TAG, help='folder if not equal to tag')
    parser.add_option('-s','--start_run', dest='start_run', type='string', default='0', help='start run')
    parser.add_option('-e','--end_run', dest='end_run', type='string', default='100000000', help='end run')
    parser.add_option('-v','--verbose', dest='verbose', action="store_true", default=False, help='verbose output')
    (options, args) = parser.parse_args()
    if options.verbose: 
        print ("options", options)
        print ("args", args)
     
    main(options.bucket, options.tag, options.folder, int(options.start_run), int(options.end_run), options.verbose)
