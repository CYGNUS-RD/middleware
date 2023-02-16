#!/usr/bin/env python3
#
# G. Mazzitelli 2022
# versione DAQ LNGS/LNF per midas file2cloud
#

import warnings

warnings.filterwarnings('ignore')

def storeStatus(filen, size, status, remotesize, outfile):
    from cygno import cmd
    stchar = ' '.join([filen, str(size), str(status), str(remotesize)])
    cmd.append2file(stchar, outfile)
    return stchar
    
def files_in_dir(in_path, ftype='mid.gz', tail_of_file=100, verbose=False):
    import os
    os.chdir(in_path)
    file_in_dir = sorted(filter(lambda file_in: file_in.endswith(ftype), os.listdir(in_path)),
                     key=os.path.getmtime)
    file_in_dir = file_in_dir[-tail_of_file:]
    return file_in_dir

def allert_mail(subject, body, mail_to, verbose):
    import os
    tmail = "echo \""+body+"\" | mutt -s \""+subject+"\" "+mail_to
    if verbose: print (tmail)
    os.system(tmail)


def main(in_path, daq_path, tag, max_tries, mail_to, verbose):
    #

    import os,sys
    import datetime
    import numpy as np
    import cygno as cy
    import time
    import midas
    import midas.client
    import gzip
    

    TIMEOUT     = 600 #secondi
    STOROUT     = daq_path+"online/log/daq_stored.log"

    print('{:s} midas2cloud started'.format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
#    max_uploed_cicle = 1 # number of maximun upload per cycle
    
    client = midas.client.MidasClient("midas2cloud")
    
    compressing_files = 0
    
    connection = cy.daq_sql_cennection(verbose)
    if not connection:
        print('{:s} ERROR: Sql connetion'.format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        sys.exit(1)
    
    while True:
        # loop on midas (ecape on midas events)
        try: 
            # compress statment
            start = time.time()
            try:
                for i, file_in in enumerate(files_in_dir(in_path, ftype='mid', tail_of_file=100, verbose=verbose)):
                    runN = int(file_in.split('run')[-1].split('.mid')[0])
                    runC = client.odb_get("/Runinfo/Run number")
                    state = client.odb_get("/Runinfo/State")
                    if (runC > runN) or state == midas.STATE_STOPPED:
#                    if not(runN == runC and state == midas.STATE_RUNNING):
#                         print("file boni "+str(runN))
                        nevent = cy.daq_run_info(connection, runN, verbose=verbose).number_of_events.values
                        if nevent == None:
                            nevent = 0
                            dtime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            print('{:s} ERROR: File badly closed, not compressed: {:s}'.format(dtime, file_in))
                        if nevent>0 and (not os.path.exists(in_path+file_in.split(".")[0]+".mid.gz")):
                            if compressing_files < 6:
                                dtime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                print('{:s} Compressing file: {:s}'.format(dtime, file_in))
                                os.system('gzip ' + in_path + file_in +' &')
                                compressing_files += 1

                if verbose : 
                    print ("Start DAQ backup at: ", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                    print ("File in dir %d" % np.size(file_in))

            except:
                print('{:s} ERROR: Compressing files'.format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

            # upload statment
            newupoload = []
            
            try:
                
                for i, file_in in enumerate(files_in_dir(in_path, ftype='mid.gz', tail_of_file=100, verbose=verbose)):
                    runN = int(file_in.split('run')[-1].split('.mid.gz')[0])
                    if cy.daq_read_runlog_replica_status(connection, runN, storage="local", verbose=verbose)==0: 

                        if not os.path.exists(in_path+file_in.split(".")[0]+".mid"):

                            dtime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                            print('{:s} Udatentig matadata for filer file: {:s}'.format(dtime, file_in))
                            filesize = os.path.getsize(in_path+file_in)               
                            md5sum = cy.cmd.md5sum_file(in_path+file_in)

                            # upadete sql with new file local status
                            cy.daq_update_runlog_replica_status(connection, 
                                                                runN, storage="local", 
                                                                status=1, verbose=verbose)
                            cy.daq_update_runlog_replica_checksum(connection, runN, 
                                                                  md5sum, verbose=verbose)
                            cy.daq_update_runlog_replica_size(connection, runN, 
                                                                  filesize, verbose=verbose)

                            dtime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            print('{:s} Transferring file: {:s}'.format(dtime, file_in))
                            compressing_files -= 1
                            current_try = 0
                            status, isthere = False, False # flag to know if to go to next run
                            #try:
                            while(not status):   
                                #tries many times for errors of connection or others that may be worth another try
                                if verbose : 
                                    print("Uploading: "+in_path+file_in)
                                    print(in_path+file_in,tag, 'cygno-data', "infncloud-wlcg", verbose, filesize)
                                if filesize < 5400000000: # ~ 5 GB
                                    dtime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                    print('{:s} Uploading file: {:s}'.format(dtime, file_in))
                                    status, isthere = cy.s3.obj_put(in_path+file_in,tag=tag, 
                                                                 bucket='cygno-data', session="infncloud-wlcg", 
                                                                 verbose=verbose)

                                    # status, isthere = True, True
                                    dtime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                    if status:
                                        if isthere:
                                            remotesize = cy.s3.obj_size(file_in,tag=tag, 
                                                             bucket='cygno-data', session="infncloud-wlcg", 
                                                             verbose=verbose)

                                            newupoload.append(storeStatus(file_in, filesize, status, 
                                                                          remotesize, STOROUT))
                                            SENDMIAL = True
                                            cy.daq_update_runlog_replica_status(connection, 
                                                                                runN, storage="cloud", 
                                                                                status=1, verbose=verbose)
                                            cy.daq_update_runlog_replica_tag(connection, runN, 
                                                                             TAG=tag, verbose=verbose)

                                            print('{:s} Upload done: {:s}'.format(dtime, file_in))
                                    else:
                                        current_try = current_try+1
                                        if current_try==max_tries:
                                            print('ERROR: Max try number reached: '+str(current_try))
                                            status=True
                                else:
                                    storeStatus(file_in, filesize, status, 0,  STOROUT)
                                    print('{:s} ERROR: File too large, not uploaded: {:s}'.format(dtime,file_in))
                                    status=True

            except:
                dtime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print('{:s} ERROR: Tranfering files: {:s}'.format(dtime,file_in))
                                      
                                      
            end = time.time()
            if len(newupoload)==0 and (end-start)>TIMEOUT and SENDMIAL:
                dtime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print('{:s} WARNING: No new file uploaded'.format(dtime))
                if mail_to != '':
                    subject = 'WARNING'
                    body = 'WARNING: no new uploaded files at '+dtime+' in last '+str(TIMEOUT)+' seconds' 
                    allert_mail(subject, body, mail_to, verbose)
                    SENDMIAL = False
                start = time.time()
            if verbose : print("\n Finished!!")

            client.communicate(10)
            time.sleep(10)

        except KeyboardInterrupt:
            client.deregister_event_request(buffer_handle, request_id)
            client.disconnect()
            print ("\nBye, bye...")
            sys.exit()


if __name__ == "__main__":
    from optparse import OptionParser
    #
    # deault parser value
    #
    TAG         = 'LNGS'
    INAPATH     = '/data01/data/'
    DAQPATH     = '/home/standard/daq/'
    max_tries   = 5
    #to = 'giovanni.mazzitelli@lnf.infn.it, davide.pinci@roma1.infn.it, francesco.renga@roma1.infn.it'
    to = 'giovanni.mazzitelli@lnf.infn.it, davide.pinci@roma1.infn.it, stefano.piacentini@uniroma1.it'

    parser = OptionParser(usage='usage: %prog [-t [{:s}] -i [{:s}]  -d [{:s}] -n [{:d}] rv]\n'.format(TAG, INAPATH,DAQPATH, max_tries))
    parser.add_option('-t','--tag', dest='tag', type='string', default=TAG, help='tag where dir for data')
    parser.add_option('-i','--inpath', dest='inpath', type='string', default=INAPATH, help='PATH to raw data')
    parser.add_option('-d','--daqpath', dest='daqpath', type='string', default=DAQPATH, help='DAQ to raw data')
    parser.add_option('-n','--tries', dest='tries', type=int, default=max_tries, help='# of retry upload temptative')
    parser.add_option('-v','--verbose', dest='verbose', action="store_true", default=False, help='verbose output')
    parser.add_option('-m','--mail', dest='mail', type='string', default=to, help='mail allert')
    (options, args) = parser.parse_args()


    max_tries   = options.tries
    verbose     = options.verbose
    to          = options.mail
    
    main(in_path=options.inpath, daq_path=options.daqpath, tag=options.tag, max_tries=options.tries, 
         mail_to=options.mail, verbose=options.verbose)
