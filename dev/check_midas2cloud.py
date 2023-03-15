#!/usr/bin/env python3
#
# G. Mazzitelli 2022
# versione DAQ LNGS/LNF per midas file2cloud 
# cheker and sql update Nov 22 
#

def main(INAPATH, TAG, fcopy, fsql, verbose):
    #

    import os,sys

    import numpy as np
    import cygno as cy
    
    import datetime

    if fsql:
        connection = cy.daq_sql_cennection(verbose)
        if not connection:
            print ("ERROR: Sql connetion")
            sys.exit(1)
    file_in_dir=sorted(os.listdir(INAPATH))
    print ("Cheching file localy and remote: ", datetime.datetime.now().time())
    print ("File in dir %d" % np.size(file_in_dir))
    for i in range(0, np.size(file_in_dir)):
        if ('run' in str(file_in_dir[i]))   and \
        ('.mid.gz' in str(file_in_dir[i]))  and \
        (not file_in_dir[i].startswith('.')):
            #
            # loop on run*.gz files
            #
            run_number = int(file_in_dir[i].split('run')[-1].split('.mid.gz')[0])
            md5sum = cy.cmd.file_md5sum(INAPATH+file_in_dir[i])
            filesize = os.path.getsize(INAPATH+file_in_dir[i])

            if (verbose): 
                print("Filename", file_in_dir[i])
                print("run_number", run_number)
                print("MD5", md5sum)          
                print("fsql", fsql)
                print("fcopy", fcopy)
            if (fsql): 
                cy.daq_update_runlog_replica_status(connection, run_number, storage="local", status=1, verbose=verbose)
                cy.daq_update_runlog_replica_checksum(connection, run_number, md5sum, verbose=verbose)
                cy.daq_update_runlog_replica_size(connection, run_number, filesize, verbose=verbose)



            remotesize = cy.s3.obj_size(file_in_dir[i],tag=TAG, 
                                     bucket='cygno-data', session="infncloud-wlcg", 
                                     verbose=verbose)
            if filesize >= 5400000000:
                print ("WARNING: file too large to be copy", file_in_dir[i], filesize)
                if (fsql):
                    cy.daq_update_runlog_replica_status(connection, run_number, 
                                                        storage="cloud", status=2, verbose=verbose)
            else:
                if (filesize != remotesize and filesize>0):
                    print ("WARNING: file size mismatch", file_in_dir[i], filesize, remotesize)
                    if (fcopy):
                        print (">>> coping file: "+file_in_dir[i])
                        status, isthere = cy.s3.obj_put(INAPATH+file_in_dir[i],tag=TAG, 
                                                     bucket='cygno-data', session="infncloud-wlcg", 
                                                     verbose=verbose)
                        if verbose: print (">>> status: ", status, "sql:", fsql)
                        if (not status and fsql):
                            cy.daq_update_runlog_replica_status(connection, run_number, 
                                                                storage="cloud", status=1, verbose=verbose)
                            cy.daq_update_runlog_replica_tag(connection, run_number, TAG=TAG, verbose=verbose)
                        else:
                            print ("ERROR: Copy on S3 faliure")
                else:
                    print ("File ", file_in_dir[i], " ok")
                    if (fsql):
                        cy.daq_update_runlog_replica_status(connection, run_number, 
                                                            storage="cloud", status=1, verbose=verbose)
                        cy.daq_update_runlog_replica_tag(connection, run_number, TAG=TAG, verbose=verbose)

                
    sys.exit(0)
if __name__ == "__main__":
    from optparse import OptionParser
    #
    # deault parser value
    #
    TAG         = 'LNGS'
    INAPATH     = '/data01/data/'


    parser = OptionParser(usage='usage: %prog [-t [{:s}] -i [{:s}] -csv]\n'.format(TAG,INAPATH))
    parser.add_option('-i','--inpath', dest='inpath', type='string', default=INAPATH, help='PATH to raw data')
    parser.add_option('-t','--tag', dest='tag', type='string', default=TAG, help='tag where dir for data')
    parser.add_option('-c','--copy', dest='copy', action="store_true", default=False, help='upload data on S3 if error')
    parser.add_option('-s','--sql', dest='sql', action="store_true", default=False, help='update sql')
    parser.add_option('-v','--verbose', dest='verbose', action="store_true", default=False, help='verbose output')
    (options, args) = parser.parse_args()
    if options.verbose: 
        print ("opions", options)
        print ("args", args)
     
    main(options.inpath, options.tag, options.copy, options.sql, options.verbose)