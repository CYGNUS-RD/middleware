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


def main(flist, bucket, tag, fcopy, fsql, fforce, verbose):
    #

    import os,sys

    import numpy as np
    import cygno as cy
    
    import time
    import subprocess
    import mysql.connector
    script_path = os.path.dirname(os.path.realpath(__file__))
    start = end = time.time()
    tmpout = '/tmp/tmp_data2save_fromlist.dat'
    tape_path = 'davs://xfer-archive.cr.cnaf.infn.it:8443/cygno/'
    if fsql or not fforce:
        connection = cy.daq_sql_cennection(verbose)
        if not connection:
            print ("ERROR: Sql connetion")
            sys.exit(1)
    client_id     = os.environ['IAM_CLIENT_ID']
    client_secret = os.environ['IAM_CLIENT_SECRET']
    endpoint_url  = os.environ['ENDPOINT_URL']
    tape_token_file  = os.environ['TAPE_TOKEN_FILE']
    s3_token_file  = os.environ['S3_TOKEN_FILE']
    
    runs = cy.daq_not_on_tape_runs(connection, verbose=verbose) 
    print("missing runs", runs)    
    
    key = tag+'/'
    with open(flist) as f:
    	files = [line.rstrip('\n') for line in f]

    for i, file_in in enumerate(files):

        run_number = int(file_in.split('run')[-1].split('.')[0])
        if (verbose): 
            print ("-------------------------")
            print (">>> ",file_in, run_number)
        if not fforce and cy.daq_read_runlog_replica_status(connection, run_number, storage="tape", verbose=verbose)==1:
                print ("File ", file_in, " ok, nothing done")
        else:
            # refresh tokens
            with open(s3_token_file) as file:
                s3_token = file.readline().strip('\n')
            if (verbose): print("s3 token: "+s3_token)

            with open(tape_token_file) as file:
                token = file.readline().strip('\n')
            os.environ["BEARER_TOKEN"] = token
            if (verbose): print("tape token: "+token)

            s3 = get_s3_client(client_id, client_secret, endpoint_url, s3_token)
            # filesize = int(cy.s3.obj_size(file_in, tag=tag, bucket=bucket, session=session, verbose=verbose))
            try:
                filesize = int(s3.head_object(Bucket=bucket,Key=key+file_in)['ContentLength'])
            except Exception as e: 
                print("ERROR in file size:", e)
                filesize = 0
            if (verbose): 
                print("Cloud name", file_in)
                print("run_number", run_number) 
                print("Cloud size", filesize, kb2valueformat(filesize))
                print("SQL actual status", 
                      cy.daq_read_runlog_replica_status(connection, run_number, storage="tape", verbose=verbose))
 
            try:
                tape_data_file = subprocess.check_output("gfal-ls -l "+tape_path\
                                 +tag+"/"+file_in+" | awk '{print $5\" \"$9}'", shell=True)

                remotesize, tape_file = tape_data_file.decode("utf-8").split(" ")
                remotesize = int(remotesize)
            except Exception as e: 
                print("WARNING/EROOR in tape size:", e)
                remotesize=0
                tape_file=file_in
                
            if (verbose): 
                print("gfal-ls -l "+tape_path\
                                 +tag+"/"+file_in+" | awk '{print $5\" \"$9}'")
                print("Tape", tape_file) 
                print("Tape size", remotesize)


            if (filesize != remotesize) and (filesize>0) or fforce:
                print ("WARNING: file size mismatch", file_in, filesize, remotesize)
                if (fcopy):
                    print (">>> coping file: "+file_in)
                    try:
                        s3.download_file(bucket, key+file_in, tmpout)
                        if (remotesize):
                            tape_data_copy = subprocess.check_output("gfal-rm "+tape_path\
                                             +tag+"/"+file_in, shell=True)
                        tape_data_copy = subprocess.check_output("gfal-copy "+tmpout+" "+tape_path\
                                     +tag+"/"+file_in, shell=True)

                        cy.cmd.rm_file(tmpout)

                        if (fsql):
                            cy.daq_update_runlog_replica_status(connection, run_number, 
                                                                storage="tape", status=1, verbose=verbose)
                            cy.daq_update_runlog_replica_tag(connection, run_number, tag, verbose=verbose)
                    except Exception as e:
                        print("ERROR: Copy on TAPE faliure", e)
            else:
                print ("File ", file_in, " ok")
                if (fsql):
                    cy.daq_update_runlog_replica_status(connection, run_number, 
                                                        storage="tape", status=1, verbose=verbose)


    sys.exit(0)
    
    
if __name__ == "__main__":
    from optparse import OptionParser
    #
    # deault parser value
    #
    TAG         = 'LNGS'
    BUCKET      = 'cygno-data'
    SESSION     = 'infncloud-wlcg'


    parser = OptionParser(usage='usage: %prog [-b [{:s}] -t [{:s}] -s[{:s}] -csv]\n'.format(BUCKET,TAG,SESSION))
    parser.add_option('-b','--bucket', dest='bucket', type='string', default=BUCKET, help='PATH to raw data')
    parser.add_option('-t','--tag', dest='tag', type='string', default=TAG, help='tag where dir for data')
    parser.add_option('-c','--copy', dest='copy', action="store_true", default=False, help='upload data to TAPE if not present')
    parser.add_option('-q','--sql', dest='sql', action="store_true", default=False, help='update sql')
    parser.add_option('-f','--force', dest='force', action="store_true", default=False, help='force full recheck of data')
    parser.add_option('-v','--verbose', dest='verbose', action="store_true", default=False, help='verbose output')
    (options, args) = parser.parse_args()
    if options.verbose: 
        print ("options", options)
        print ("args", args)
    if len(args)<1:
        parser.error("file list name missing")
        sys.exit(1)
    main(args[0], options.bucket, options.tag, options.copy, options.sql, options.force, options.verbose)
