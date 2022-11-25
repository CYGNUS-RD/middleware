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
    import midas
    import midas.client
    import gzip
    
    #
    # deault parser value
    #
    TAG         = 'LNGS'
    INAPATH     = '/data01/data/'
    DAQPATH     = '/home/standard/daq/'
    max_tries   = 5
    #to = 'giovanni.mazzitelli@lnf.infn.it, davide.pinci@roma1.infn.it, francesco.renga@roma1.infn.it'
    to = ''

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
     
    INAPATH    = options.inpath
    DAQPATH    = options.daqpath

    STOROUT    = DAQPATH+"online/daq_stored.log"
    FILELOK    = INAPATH+"analized.lok"
    newupoload = []
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
            file_in_dir=sorted(os.listdir(INAPATH))
            try:

                if verbose : print ("Start DAQ backup at: ", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                if verbose : print ("File in dir %d" % np.size(file_in_dir))

                ipload = 1 # index of file uploaded
                # if verbose : print(file_in_dir)

                for i in range(0, np.size(file_in_dir)):
                    if ('run' in str(file_in_dir[i]))   and \
                    ('.mid' in str(file_in_dir[i]))  and \
                    (not ('.gz' in str(file_in_dir[i]))) and \
                    (not('.crc32c' in str(file_in_dir[i]))) and\
                    ((str(file_in_dir[i]).split('.mid')[0] + '.crc32c') in file_in_dir) and \
                    (not ( (str(file_in_dir[i]) + '.gz') in file_in_dir)) and \
                    (not file_in_dir[i].startswith('.')):
                        if compressing_files < 6:
                            dtime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            print('{:s} Compressing file: {:s}'.format(dtime, file_in_dir[i]))
                            os.system('gzip ' + INAPATH + file_in_dir[i] +' &')
                            compressing_files += 1
            except:
                print('{:s} ERROR: Compressing files'.format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            # upload statment

            for i in range(0, np.size(file_in_dir)):
                if ('run' in str(file_in_dir[i]))   and \
                ('.mid.gz' in str(file_in_dir[i]))  and \
                (not (str(file_in_dir[i]).split('.gz')[0] in file_in_dir)) \
                and (not file_in_dir[i].startswith('.')):

                    if cy.cmd.grep_file(file_in_dir[i], STOROUT) == "": # da sotituire con il check nell'sql 
                        
                        dtime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        
                        print('{:s} Udatentig matadata for filer file: {:s}'.format(dtime, file_in_dir[i]))
                        filesize = os.path.getsize(INAPATH+file_in_dir[i])               
                        runN = int(file_in_dir[i].split('run')[-1].split('.mid.gz')[0])
                        md5sum = cy.cmd.file_md5sum(INAPATH+file_in_dir[i])
                        runC = client.odb_get("/Runinfo/Run number")
                        state = client.odb_get("/Runinfo/State")


                        if verbose: 
                            print(runN, runC, state)

                        # upadete sql with new file local status
                        cy.daq_update_runlog_replica_status(connection, 
                                                            runN, storage="local", 
                                                            status=1, verbose=verbose)
                        cy.daq_update_runlog_replica_checksum(connection, runN, 
                                                              md5sum, verbose=verbose)
                        cy.daq_update_runlog_replica_size(connection, runN, 
                                                              filesize, verbose=verbose)

                        if not(runN == runC and state == midas.STATE_RUNNING) or midas.STATE_STOPPED:
                            dtime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            print('{:s} Transferring file: {:s}'.format(dtime, file_in_dir[i]))
                            compressing_files -= 1
                            current_try = 0
                            status, isthere = False, False # flag to know if to go to next run
                            try:
                                while(not status):   
                                    #tries many times for errors of connection or others that may be worth another try
                                    if verbose : 
                                        print("Uploading: "+INAPATH+file_in_dir[i])
                                        print(INAPATH+file_in_dir[i],TAG, 'cygno-data', "infncloud-wlcg", verbose, filesize)
                                    if filesize < 5400000000: # ~ 5 GB
                                        dtime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                        print('{:s} Uploading file: {:s}'.format(dtime, file_in_dir[i]))
                                        status, isthere = cy.s3.obj_put(INAPATH+file_in_dir[i],tag=TAG, 
                                                                     bucket='cygno-data', session="infncloud-wlcg", 
                                                                     verbose=verbose)

                                        # status, isthere = True, True
                                        dtime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                        if status:
                                            if isthere:
                                                remotesize = cy.s3.obj_size(file_in_dir[i],tag=TAG, 
                                                                 bucket='cygno-data', session="infncloud-wlcg", 
                                                                 verbose=verbose)

                                                newupoload.append(storeStatus(file_in_dir[i], filesize, status, 
                                                                              remotesize, STOROUT))
                                                cy.daq_update_runlog_replica_status(connection, 
                                                                                    runN, storage="cloud", 
                                                                                    status=1, verbose=verbose)
                                                cy.daq_update_runlog_replica_tag(connection, runN, 
                                                                                 TAG=TAG, verbose=verbose)

                                                print('{:s} Upload done: {:s}'.format(dtime, file_in_dir[i]))
                                                ipload+=1
                                        else:
                                            current_try = current_try+1
                                            if current_try==max_tries:
                                                print('ERROR: Max try number reached: '+str(current_try))
                                                status=True
                                    else:
                                        storeStatus(file_in_dir[i], filesize, status, 0,  STOROUT)
                                        print('{:s} ERROR: File too large, not uploaded: {:s}'.format(dtime,file_in_dir[i]))
                                        status=True
                            except:
                                dtime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                print('{:s} ERROR: Tranfering files: {:s}'.format(dtime,file_in_dir[i]))
                                      
                                      
                    if verbose: print("file alredy uploaded or size ok")
                
            if len(newupoload)==0:
                dtime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print('{:s} WARNING: No new file uploaded'.format(dtime))

            if to != '':
                when = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                subject = "latest news fro DAQ!"
                if len(newupoload)>0:
                    body = 'last files uploaded at '+when+': '+str([s for s in newupoload])
                    # allert_mail(subject, body, to, verbose)
                else:
                    body = 'WARNING: no new uploaded files at '+when
                    allert_mail(subject, body, to, verbose)
            if verbose : print("\n Finished!!")

            client.communicate(10)
            time.sleep(10)

        except KeyboardInterrupt:
            client.deregister_event_request(buffer_handle, request_id)
            client.disconnect()
            print ("\nBye, bye...")
            sys.exit()


if __name__ == "__main__":
    main()
