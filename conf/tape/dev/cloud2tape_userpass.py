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

def get_s3_client(user, passw, endpoint_url):
    import boto3
    import os
    credentials = boto3.session.Session(
        aws_access_key_id=user,
        aws_secret_access_key=passw
    )
    s3 = credentials.client('s3', endpoint_url=endpoint_url,
                            config=boto3.session.Config(signature_version='s3v4'),verify=True)

#    print(s3)
    return s3



def main(bucket, tag, fcopy, fsql, fforce, verbose):
    #

    import os,sys

    import numpy as np
    import cygno as cy
    
    import time
    import subprocess
    import mysql.connector
    script_path = os.path.dirname(os.path.realpath(__file__))
    start = end = time.time()
    #tmpout = '/tmp/tmp_data2save_'+tag+'.dat'
    tape_path = 'davs://xfer-archive.cr.cnaf.infn.it:8443/cygno/'
    if fsql or not fforce:
        connection = cy.daq_sql_cennection(verbose)
        if not connection:
            print ("ERROR: Sql connetion")
            sys.exit(1)
    user     = os.environ['BA_ACCESS_KEY_ID']
    passw    = os.environ['BA_SECRET_ACCESS_KEY']
    endpoint_url  = os.environ['ENDPOINT_URL']
    tape_token_file  = os.environ['TAPE_TOKEN_FILE']
    
    runs = cy.daq_not_on_tape_runs(connection, verbose=verbose) 
    print("missing runs:", len(runs), runs)    
    
    key = tag+'/'
    
    for i, run in enumerate(runs):
        file_in="run{:05d}.mid.gz".format(run)
        if (verbose): 
            print("-------------------------")
        run_number = run
        tmpout = '/tmp/tag_'+file_in
	
        if not fforce and cy.daq_read_runlog_replica_status(connection, run_number, storage="tape", verbose=verbose)==1:
                print ("File ", file_in, " ok, nothing done")
        else:
            with open(tape_token_file) as file:
                token = file.readline().strip('\n')
            os.environ["BEARER_TOKEN"] = token
            if (verbose): print("tape token: "+token)

            s3 = get_s3_client(user, passw, endpoint_url)
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
                print("SQL actual status", cy.daq_read_runlog_replica_status(connection, 
                                                                             run_number, 
                                                                             storage="tape", 
                                                                             verbose=verbose))
 
            try:
                tape_data_file = subprocess.check_output("gfal-ls -l "+tape_path\
                                 +bucket+"/"+tag+"/"+file_in+" | awk '{print $5\" \"$9}'", shell=True)

                remotesize, tape_file = tape_data_file.decode("utf-8").split(" ")
                remotesize = int(remotesize)
            except Exception as e: 
                print("WARNING/EROOR in tape size:", e)
                remotesize=0
                tape_file=file_in
                
            if (verbose): 
                print("gfal-ls -l "+tape_path\
                                 +bucket+"/"+tag+"/"+file_in+" | awk '{print $5\" \"$9}'")
                print("Tape", tape_file) 
                print("Tape size", remotesize)


            if (filesize != remotesize) and (filesize>0) or fforce:
                if not fforce: print ("WARNING: file size mismatch", file_in, filesize, remotesize)
                if (fcopy):
                    print (">>> coping file: "+file_in)
                    try:
                        s3.download_file(bucket, key+file_in, tmpout)
                    except Exception as e:
                        print("ERROR: Donwnload faliure", e)
                    try:
                        if (remotesize):
                            tape_data_copy = subprocess.check_output("gfal-rm "+tape_path\
                                             +bucket+"/"+tag+"/"+file_in, shell=True)
                        tape_data_copy = subprocess.check_output("gfal-copy "+tmpout+" "+tape_path\
                                     +bucket+"/"+tag+"/"+file_in, shell=True)

                        cy.cmd.rm_file(tmpout)

                        if (fsql):
                            s1 = cy.daq_update_runlog_replica_status(connection, run_number, 
                                                    storage="tape", status=1, verbose=verbose)
                            
                            s2 = cy.daq_update_runlog_replica_tag(connection, run_number, 
                                                                  tag, verbose=verbose)
                            if s2<0 or s1<0:
                                print("ERROR: SQL faliure", s1, s2)
                                sys.exit(1)
                    except Exception as e:
                        print("ERROR: Copy on TAPE faliure", e)
            else:
                print ("File ", file_in, " ok")
                if (fsql):
                    s3 = cy.daq_update_runlog_replica_status(connection, run_number, 
                                                        storage="tape", status=1, verbose=verbose)
                    if s3<0:
                        print("ERROR: SQL faliure", s1, s2)
                        sys.exit(1)


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
     
    main(options.bucket, options.tag, options.copy, options.sql, options.force, options.verbose)

