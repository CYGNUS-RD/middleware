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


def main(bucket, key, copy, remove, verbose):
    #

    import os,sys

    import numpy as np
    import cygno as cy
    
    import time
    import subprocess
    import boto3
    from boto3.s3.transfer import TransferConfig
    
    script_path = os.path.dirname(os.path.realpath(__file__))
    start = end = time.time()

# tape setup
    tape_path = 'davs://xfer-archive.cr.cnaf.infn.it:8443/cygno/'

    client_id     = os.environ['IAM_CLIENT_ID']
    client_secret = os.environ['IAM_CLIENT_SECRET']
    endpoint_url  = os.environ['ENDPOINT_URL']
    tape_token_file  = os.environ['TAPE_TOKEN_FILE']
    s3_token_file  = os.environ['S3_TOKEN_FILE']

# BA S3 storage
    
    ba_session = boto3.session.Session(
        aws_access_key_id=os.environ.get('BA_ACCESS_KEY_ID'),
        aws_secret_access_key=os.environ.get('BA_SECRET_ACCESS_KEY')
    )

    s3_ba = ba_session.client('s3', endpoint_url="https://swift.recas.ba.infn.it/",
                            config=boto3.session.Config(signature_version='s3v4'),verify=True)

    GB = 1024 ** 3
    config = TransferConfig(multipart_threshold=5*GB)
    
#####################
    
    with open(s3_token_file) as file:
        s3_token = file.readline().strip('\n')
    if (verbose): print("s3 token: "+s3_token)
    s3 = get_s3_client(client_id, client_secret, endpoint_url, s3_token)
    
    print('--> listing files, plese wait')
    files = bucket_list(s3, key=key, bucket=bucket, filearray=True, verbose=False)
    # if verbose: 
    #     print(files)
    print('-------------')
    n_file = len(files)
    print('number of files', n_file)
    # if remove:
    #     answer = input("you are going to remove orginals files, continue (explicity write y/yes)? ")
    #     if answer.lower() in ["y","yes"]:
    #          print('--> starting')
    #     else:
    #          sys.exit(0)

    
    for i, filepath in enumerate(files):
        file_in = filepath.split('/')[-1]
        tmpout = '/tmp/'+file_in 
        print("-------------------------")
        # print(file_in, filepath)
        
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
# check file on tape
        try:
            tape_data_file = subprocess.check_output("gfal-ls -l "+tape_path\
                             +bucket+'/'+filepath+" | awk '{print $5\" \"$9}'", shell=True)

            remotesize, tape_file = tape_data_file.decode("utf-8").split(" ")
            remotesize = int(remotesize)

        except Exception as e: 
#            print("WARNING no file on TAPE:", e)
            remotesize=0
            tape_file=file_in
        if (verbose): print("remotesize: ", remotesize)
# check file on BA
        basize = 0
        if copy:
            results = s3_ba.list_objects(Bucket=bucket, Prefix=bucket+'/'+filepath)
            if 'Contents' in results:
                basize = int(results['Contents'][0]['Size'])
            if (verbose): print("basize: ", basize, results)
           # else:
           # print("WARNING no file on BA S3:")
            

            
        # if (verbose): 
        #     print("gfal-ls -l "+tape_path+bucket+'/'+filepath+" | awk '{print $5\" \"$9}'")
        #     print("Tape", tape_file) 
        #     print("Tape size", remotesize)

        if ((filesize != remotesize) or (filesize != basize)) and (filesize>0) :
            if verbose: print('>>>',file_in, filesize, remotesize, basize, i, n_file)
            print ("file: {:s} {:d} {:d} {:d} {:d}/{:d}".format(file_in, filesize, remotesize, basize, i, n_file))
            
            try:
                if verbose: print("file download", filepath, tmpout) 
                s3.download_file(bucket, filepath, tmpout)
            except Exception as e:
                print("ERROR: Download faliure: ", e)
                sys.exit(2)
                
            if (filesize != remotesize):
                try:
                    if (remotesize):
                        tape_data_copy = subprocess.check_output("gfal-rm "+tape_path+bucket+'/'+filepath, shell=True)
                    if verbose: print("upload TAPE", tmpout, filepath)
                    tape_data_copy = subprocess.check_output("gfal-copy "+tmpout+" "+tape_path+bucket+'/'+filepath, shell=True)
                except Exception as e:
                    print("ERROR: Copy on TAPE faliure: ", e)
                    sys.exit(3)
                
            if (filesize != basize) and copy:
                try:
                    if verbose: print("upload BA S#", tmpout, filepath)
                    s3_ba.upload_file(tmpout, Bucket=bucket, Key=filepath, Config=config)
                except Exception as e:
                    print("ERROR: Copy on BA S3 faliure: ", e)
                    sys.exit(4)
                    
            cy.cmd.rm_file(tmpout)
            try:
                tape_data_file = subprocess.check_output("gfal-ls -l "+tape_path\
                                +bucket+'/'+filepath+" | awk '{print $5\" \"$9}'", shell=True)
    
                remotesize, tape_file = tape_data_file.decode("utf-8").split(" ")
                remotesize = int(remotesize)      
                if copy:
                    basize = int(s3_ba.head_object(Bucket=bucket, Key=filepath)['ContentLength'])
                else:
                    basize = filesize # cosi che rimuova comunque se la flag remove e True.
                if (filesize == remotesize) and (filesize == basize) and remove:
                    response = s3.delete_object(Bucket=bucket, Key=filepath)
                    print ('removed file:', filepath, kb2valueformat(filesize))
            except Exception as e:
                print("ERROR: Checking file on remote", e)
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

    parser = OptionParser(usage='usage: %prog [-b [{:s}] <path> options: -c copy to BA S3 -r remove orginal files -v verbose]\n'.format(BUCKET))
    parser.add_option('-b','--bucket', dest='bucket', type='string', default=BUCKET, help='source bucket')
    parser.add_option('-c','--copy', dest='copy', action='store_true', default=False, help='copy on backup S3')
    parser.add_option('-r','--remove', dest='remove', action='store_true', default=False, help='remove file')
    parser.add_option('-v','--verbose', dest='verbose', action="store_true", default=False, help='verbose output')
    (options, args) = parser.parse_args()
    if options.verbose: 
        print ("options", options)
        print ("args", args)
    if len(args)<1:
        parser.error("missing key/folder to beckup, example {:s}".format(KEY))
        sys.exit(1)
     
    main(options.bucket, args[0], options.copy, options.remove, options.verbose)
