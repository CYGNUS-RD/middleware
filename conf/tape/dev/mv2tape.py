#!/usr/bin/env python3
#
# G. Mazzitelli 2022
# versione DAQ LNGS/LNF per midas copy/check/or mouve files from cloud cloud to tape 
# 
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



def main(bucket, key, remove, verbose):
    #

    import os,sys

    import numpy as np
    import cygno as cy
    
    import time
    import subprocess
    script_path = os.path.dirname(os.path.realpath(__file__))
    start = end = time.time()
    

    tape_path = 'davs://xfer-archive.cr.cnaf.infn.it:8443/cygno/'

    client_id     = os.environ['IAM_CLIENT_ID']
    client_secret = os.environ['IAM_CLIENT_SECRET']
    endpoint_url  = os.environ['ENDPOINT_URL']
    tape_token_file  = os.environ['TAPE_TOKEN_FILE']
    s3_token_file  = os.environ['S3_TOKEN_FILE']
    
    
    with open(s3_token_file) as file:
        s3_token = file.readline().strip('\n')
    if (verbose): print("s3 token: "+s3_token)
    s3 = get_s3_client(client_id, client_secret, endpoint_url, s3_token)
    
    print('--> listing files, plese wait')
    files = bucket_list(s3, key=key, bucket=bucket, filearray=True, verbose=False)
    if verbose: 
        print(files)
    print('-------------')
    print('number of files', len(files))
    if remove:
        answer = input("you are going to remove orginals files, continue (explicity write y/yes)? ")
        if answer.lower() in ["y","yes"]:
             print('--> starting')
        else:
             sys.exit(0)

    
    for i, filepath in enumerate(files):
        file_in = filepath.split('/')[-1]
        tmpout = '/tmp/'+file_in 
        print("-------------------------")
        print(file_in, filepath)
	
        with open(s3_token_file) as file:
            s3_token = file.readline().strip('\n')
        if (verbose): print("s3 token: "+s3_token)

        with open(tape_token_file) as file:
            token = file.readline().strip('\n')
        os.environ["BEARER_TOKEN"] = token
        if (verbose): print("tape token: "+token)

        s3 = get_s3_client(client_id, client_secret, endpoint_url, s3_token)

        try:
            filesize = int(s3.head_object(Bucket=bucket,Key=filepath)['ContentLength'])
        except Exception as e: 
            print("ERROR in file size:", e)
            sys.exit(1)
            
        if (verbose): 
            print("Cloud name", file_in)
            print("Cloud size", filesize, kb2valueformat(filesize))

        try:
            tape_data_file = subprocess.check_output("gfal-ls -l "+tape_path\
                             +filepath+" | awk '{print $5\" \"$9}'", shell=True)

            remotesize, tape_file = tape_data_file.decode("utf-8").split(" ")
            remotesize = int(remotesize)
        except Exception as e: 
            print("WARNING in tape size:", e)
            remotesize=0
            tape_file=file_in
            
        if (verbose): 
            print("gfal-ls -l "+tape_path+filepath+" | awk '{print $5\" \"$9}'")
            print("Tape", tape_file) 
            print("Tape size", remotesize)


        if (filesize != remotesize) and (filesize>0):
            print ("WARNING: file size mismatch", file_in, filesize, remotesize)
            try:
                s3.download_file(bucket, filepath, tmpout)
                print("file download", filepath, tmpout)
                
            except Exception as e:
                print("ERROR: Download faliure: ", e)
                sys.exit(2)
            try:
                if (remotesize):
                    tape_data_copy = subprocess.check_output("gfal-rm "+tape_path+filepath, shell=True)
                tape_data_copy = subprocess.check_output("gfal-copy "+tmpout+" "+tape_path+filepath, shell=True)

                cy.cmd.rm_file(tmpout)
            except Exception as e:
                print("ERROR: Copy on TAPE faliure: ", e)
                sys.exit(3)
            try:
                tape_data_file = subprocess.check_output("gfal-ls -l "+tape_path\
                                +filepath+" | awk '{print $5\" \"$9}'", shell=True)
    
                remotesize, tape_file = tape_data_file.decode("utf-8").split(" ")
                remotesize = int(remotesize)         
                if (filesize == remotesize) and remove:
                    response = s3.delete_object(Bucket=bucket,Key=filepath)
                    print ('removed file: '+filepath)
            except Exception as e:
                print("ERROR: Copy on TAPE faliure", e)
                sys.exit(3)
        else:
            print("recheck ok")

    sys.exit(0)
    
    
if __name__ == "__main__":
    from optparse import OptionParser
    #
    # deault parser value
    #
    KEY         = 'RECO/Winter23/'
    BUCKET      = 'cygno-analysis'

    parser = OptionParser(usage='usage: %prog [-b [{:s}] -r remove orginal files -v verbose]\n'.format(BUCKET))
    parser.add_option('-b','--bucket', dest='bucket', type='string', default=BUCKET, help='PATH to raw data')
    parser.add_option('-r','--remove', dest='remove', action='store_true', default=False, help='remove file')
    parser.add_option('-v','--verbose', dest='verbose', action="store_true", default=False, help='verbose output')
    (options, args) = parser.parse_args()
    if options.verbose: 
        print ("options", options)
        print ("args", args)
    if len(args)<1:
        parser.error("missing key/folder to beckup, example {:s}".format(KEY))
        sys.exit(1)
     
    main(options.bucket, args[0], options.remove, options.verbose)
