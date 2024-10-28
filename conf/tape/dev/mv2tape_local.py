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

def main(dir, remove, verbose):
    #

    import os,sys

    import numpy as np
    import cygno as cy
    
    import time
    import subprocess

    script_path = os.path.dirname(os.path.realpath(__file__))

    tape_path = 'davs://xfer-archive.cr.cnaf.infn.it:8443/cygno'

    client_id     = os.environ['IAM_CLIENT_ID']
    client_secret = os.environ['IAM_CLIENT_SECRET']
    endpoint_url  = os.environ['ENDPOINT_URL']
    tape_token_file  = os.environ['TAPE_TOKEN_FILE']

#    files = os.listdir(dir)
#    if verbose: 
#        print(files)
#    print('-------------')
#    print('number of files', len(files))
    if remove:
        answer = input("you are going to remove orginals files, continue (explicity write y/yes)? ")
        if answer.lower() in ["y","yes"]:
             print('--> starting')
        else:
             sys.exit(0)

#    for i, file in enumerate(files):
#        filepath = dir+file
#        print(file, filepath)
    start = time.time()
    timerefresh = elapsed = 1200
    for path, subdirs, files in os.walk(dir):
        for name in files:
            filepath=os.path.join(path, name)

            if elapsed>=timerefresh:
               with open(tape_token_file) as file:
                  token = file.readline().strip('\n')
               os.environ["BEARER_TOKEN"] = token
               start = time.time()
               if (verbose): print("tape token: "+token)
            elapsed = int(time.time() - start)

            try:
               filesize = os.stat(filepath).st_size
            except Exception as e: 
               print("ERROR in file size:", e)
               sys.exit(1)

            if (verbose):
               print("Local name", name, filepath)
               print("Local size", filesize, kb2valueformat(filesize))

            try:
               tape_data_file = subprocess.check_output("gfal-ls -l "+tape_path\
                             +filepath+" | awk '{print $5\" \"$9}'", shell=True)

               remotesize, tape_file = tape_data_file.decode("utf-8").split(" ")
               remotesize = int(remotesize)
            except Exception as e: 
               print("WARNING in tape size:", e)
               remotesize=0
               tape_file=file

            if (verbose): 
               print("gfal-ls -l "+tape_path+filepath+" | awk '{print $5\" \"$9}'")
               print("Tape", tape_file) 
               print("Tape size", remotesize)


            if (filesize != remotesize) and (filesize>0):
                print ("WARNING: file size mismatch", file, filesize, remotesize)
                try:
                    if (remotesize):
                        tape_data_copy = subprocess.check_output("gfal-rm "+tape_path+filepath, shell=True)
                    tape_data_copy = subprocess.check_output("gfal-copy "+filepath+" "+tape_path+filepath, shell=True)

                except Exception as e:
                    print("ERROR: Copy on TAPE faliure: ", e)
                    sys.exit(3)
                try:
                    tape_data_file = subprocess.check_output("gfal-ls -l "+tape_path\
                                +filepath+" | awk '{print $5\" \"$9}'", shell=True)

                    remotesize, tape_file = tape_data_file.decode("utf-8").split(" ")
                    remotesize = int(remotesize)         
                    if (filesize == remotesize) and remove:
                        response = os.remove(filepath)
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
    DIR       = '/nfs/cygno/'

    parser = OptionParser(usage='usage: %prog <dirctory> -r remove orginal files -v verbose]\n')
    parser.add_option('-r','--remove', dest='remove', action='store_true', default=False, help='remove file')
    parser.add_option('-v','--verbose', dest='verbose', action="store_true", default=False, help='verbose output')
    (options, args) = parser.parse_args()
    if options.verbose: 
        print ("options", options)
        print ("args", args)
    if len(args)<1:
        parser.error("missing folder to beckup, example {:s}".format(DIR))
        sys.exit(1)
     
    main(args[0], options.remove, options.verbose)
