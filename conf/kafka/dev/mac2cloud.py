#!/usr/bin/env python3
#
# G. Mazzitelli 2022
# versione DAQ LNGS/LNF per midas file2cloud
#
def storeStatus(filen, size, status, remotesize, outfile):
    from cygno import cmd
    stchar = ' '.join([filen, str(size), str(status), str(remotesize)])
    cmd.append2file(stchar, outfile)
    return stchar
    
def main():
    #
    from optparse import OptionParser
    import os,sys
    import datetime
    import numpy as np
    import cygno as cy
    import time
    
    #
    # deault parser value
    #
    TAG         = "WC"
    INAPATH     = "./loop/"
    DAQPATH     = "./"
    session     = "sentinel-wlcg"
    bucket      = "cygno-analysis"
    max_tries   = 5

    parser = OptionParser(usage='usage: %prog [-t [{:s}] -i [{:s}]  -n [{:d}] rv]\n'.format(TAG, INAPATH, max_tries))
    parser.add_option('-t','--tag', dest='tag', type='string', default=TAG, help='tag where dir for data')
    parser.add_option('-i','--inpath', dest='inpath', type='string', default=INAPATH, help='PATH to raw data')
    parser.add_option('-d','--daqpath', dest='daqpath', type='string', default=DAQPATH, help='log folder')
    parser.add_option('-n','--tries', dest='tries', type=int, default=max_tries, help='# of retry upload temptative')
    parser.add_option('-v','--verbose', dest='verbose', action="store_true", default=False, help='verbose output')
    parser.add_option('-s','--session', dest='session', type='string', default=session, help='session [infncloud-iam]')
    (options, args) = parser.parse_args()


    max_tries   = options.tries
    verbose     = options.verbose
    session     = options.session
     
    INAPATH    = options.inpath
    DAQPATH    = options.daqpath

    STOROUT    = DAQPATH+"/stored.log"

    newupoload = []
    print('{:s} mc2cloud started'.format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    
    while True:
        # loop on midas (ecape on midas events)
        try: 
            file_in_dir=os.listdir(INAPATH)
            print(file_in_dir)
            for i in range(0, np.size(file_in_dir)): #
                print(file_in_dir[i])
                if ('.csv' in str(file_in_dir[i])) and (not file_in_dir[i].startswith('.')):
                    if cy.cmd.grep_file(file_in_dir[i], STOROUT) == "": 
                        filesize = os.path.getsize(INAPATH+file_in_dir[i]) 
                        dtime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        if verbose:              
                            print('{:s} Transferring file: {:s}'.format(dtime, file_in_dir[i]))
                        current_try = 0
                        status, isthere = False, False # flag to know if to go to next run
                        while(not status):   
                            #tries many times for errors of connection or others that may be worth another try
                            if verbose : 
                                print(INAPATH+file_in_dir[i],TAG, bucket, session, verbose, filesize)
                            status, isthere = cy.s3.obj_put(INAPATH+file_in_dir[i],tag=TAG, 
                                                         bucket=bucket, session=session, 
                                                         verbose=verbose)
                            if status:
                                if isthere:
                                    remotesize = cy.s3.obj_size(file_in_dir[i],tag=TAG, 
                                                     bucket=bucket, session=session, 
                                                     verbose=verbose)

                                    newupoload.append(storeStatus(file_in_dir[i], filesize, status, 
                                                                  remotesize, STOROUT))

                                    cy.cmd.rm_file(INAPATH+file_in_dir[i])
                                    if verbose:              
                                        print('{:s} file removed: {:s}'.format(dtime, file_in_dir[i]))

                                    ##############################
                                    if verbose: 
                                        print('{:s} Upload done: {:s}'.format(dtime, file_in_dir[i]))

                            else:
                                current_try = current_try+1
                                if current_try==max_tries:
                                    print('{:s} ERROR: Max try number reached: {:d}'.format(dtime, current_try))
                                    status=True

            time.sleep(10)


        except KeyboardInterrupt:
            print ("\nBye, bye...")
            sys.exit()

if __name__ == "__main__":
    main()