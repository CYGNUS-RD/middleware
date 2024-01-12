import os
import stat

import mysql.connector
import cygno as cy
from cygno import cmd
import datetime
import subprocess

def refreshToken():
    print("Setting environment (Condor and SQL)")
    process = subprocess.Popen(
        "source ../start_script.sh", shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    process2 = subprocess.Popen(
        "source ../SQLSetup.sh", shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    output, error = process.communicate()

    #if error:
    #    raise Exception(f"Error in executing condor refresh: {error}")
        
    output2, error2 = process2.communicate()
    
    #if error:
    #    raise Exception(f"Error in executing SQLSetup: {error}") 


def reco2cloud(recofilename, recofolder, verbose=False):
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
    

def main(verbose=True):
    
    run_number_row = 17600
    #Run data2cloud
    recofilename = '%s_run%05d_%s.root' % ('reco', run_number_row, '3D')
    recofolder   =  '../submitJobs/'
    refreshToken()
    reco2cloud(recofilename, recofolder, verbose=False)
    
if __name__ == "__main__":
    from optparse import OptionParser
    parser = OptionParser(usage='usage: %prog\t ')
    parser.add_option('-v','--verbose', dest='verbose', action="store_true", default=False, help='verbose output;');
    (options, args) = parser.parse_args()
    main(verbose=options.verbose)