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


def main(tag, verbose):
    #

    import os,sys

    import numpy as np
    import subprocess
    script_path = os.path.dirname(os.path.realpath(__file__))
    tape_path = 'davs://xfer-archive.cr.cnaf.infn.it:8443/cygno/'
    client_id     = os.environ['IAM_CLIENT_ID']
    client_secret = os.environ['IAM_CLIENT_SECRET']
    endpoint_url  = os.environ['ENDPOINT_URL']
    tape_token_file  = os.environ['TAPE_TOKEN_FILE']
    s3_token_file  = os.environ['S3_TOKEN_FILE']
    
    
    with open(tape_token_file) as file:
        token = file.readline().strip('\n')
    os.environ["BEARER_TOKEN"] = token
    if (verbose): print("tape token: "+token)
    try:
        tape_data_file = subprocess.check_output("gfal-ls -l "+tape_path+tag+"/ | awk '{print $9\" \"$5}'", shell=True)
        datas = np.sort(np.array(tape_data_file.decode("utf-8").split('\n')))
        #print (type(datas), len(datas))
        
        for i, data in enumerate(datas):
            run, size = np.array(data.split(' '))
            print (i, run, size)
    except Exception as e: 
        print("WARNING/EROOR in tape size:", e)
        exit(1)
    exit(0)
    
    
if __name__ == "__main__":
    from optparse import OptionParser
    #
    # deault parser value
    #



    parser = OptionParser(usage='usage: %prog <tag> -v')
    parser.add_option('-v','--verbose', dest='verbose', action="store_true", default=False, help='verbose output')
    (options, args) = parser.parse_args()
    if options.verbose: 
        print ("options", options)
        print ("args", args)
    if len(args)<1:
        parser.print_help()
        exit(1)
    main(args[0], options.verbose)
