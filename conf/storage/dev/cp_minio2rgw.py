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

def bucket_list(s3, key, bucket='cygno-analysis', filearray=False, verbose=False):
    import boto3

    lsarray=[]
    IsTruncated = True
    NextMarker  = ''
    while IsTruncated:
        response    = s3.list_objects(Bucket=bucket, Marker=NextMarker)
        IsTruncated = response['IsTruncated']
        contents = response['Contents']
        for i, file in enumerate(contents):
            if key in str(file['Key']):
                if filearray:
                    lsarray.append(file['Key'])
                else:
                    print("{0:20s} {1:s}".format(str(file['LastModified']).split(".")[0].split("+")[0], file['Key']))
        if IsTruncated:
            Marker      = response['Marker']
            NextMarker  = response['NextMarker']
        if verbose: print("bucket troncato? "+str(IsTruncated),"Marker: ", Marker,"NextMarker: ", NextMarker)
    # return array 
    return lsarray



def main(bucket,folder, session, verbose):
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
    # s3_token_file  = os.environ['S3_TOKEN_FILE']
    s3_token_file  = "/tmp/token"
    endpoint_url = "https://minio.cloud.infn.it/"
    if verbose: print (mytoken)

    with open(s3_token_file) as file:
        s3_token = file.readline().strip('\n')
    if (verbose): print("s3 token: "+s3_token)
    s3 = get_s3_client(client_id, client_secret, endpoint_url, s3_token)

    print('--> listing files, plese wait')
    files = bucket_list(s3, key=folder, bucket=bucket, filearray=True, verbose=False)
    if verbose: 
        print(files)
    print('-------------')
    print('number of files', len(files))


    start = end = time.time()


    for i, filepath in enumerate(files):
        file_in = filepath.split('/')[-1]
        tmpout = '/tmp/'+file_in 
        print("-------------------------")
        print(file_in, filepath)

        with open(s3_token_file) as file:
            s3_token = file.readline().strip('\n')
        if (verbose): print("s3 token: "+s3_token)

        if (end-start)>3000 or (start-end)==0:
           output = subprocess.check_output("export TOKEN=$(oidc-token --aud='object'"+session+")", shell=True)
           start = time.time()
        end = time.time()
        try:
           s3.download_file(bucket, filepath, tmpout)
        except Exception as e:
           print("ERROR: Download faliure: ", e)
           sys.exit(1)
        try:
           s3_out=get_s3_client_rgw()
           s3_out.upload_file(tmpout, bucket, folder+file_in)
        except Exception as e:
           print("ERROR: upload faliure: ", e)
           sys.exit(1)
        cy.cmd.rm_file(tmpout)
    sys.exit(0)
    
    
if __name__ == "__main__":
    from optparse import OptionParser
    #
    # deault parser value
    #
    BUCKET      = 'cygno-data'
    SESSION     = 'infncloud-iam'


    parser = OptionParser(usage='usage: %prog [-b [{:s}] -s[{:s}] -csv]\n'.format(BUCKET,SESSION))
    parser.add_option('-s','--session', dest='session', type='string', default=SESSION, help='session ')
    parser.add_option('-b','--bucket', dest='bucket', type='string', default=BUCKET, help='PATH to raw data')
    parser.add_option('-v','--verbose', dest='verbose', action="store_true", default=False, help='verbose output')
    (options, args) = parser.parse_args()
    if options.verbose: 
        print ("options", options)
        print ("args", args)
     
    main(options.bucket, args[0], options.session, options.verbose)
