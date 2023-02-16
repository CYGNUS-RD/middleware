#!/usr/bin/env python3
#
# G. Mazzitelli 2022
# versione DAQ LNGS/LNF per midas file2cloud 
# cheker and sql update Nov 22 
#


def files_in_dir(in_path, ftype='mid.gz', tail_of_file=200, verbose=False):
    import os
    os.chdir(in_path)
    file_in_dir = sorted(filter(os.path.isfile, os.listdir(in_path)), key=os.path.getmtime)

    if len(file_in_dir)<tail_of_file:
        tail_of_file=len(file_in_dir)
    file_in_dir = file_in_dir[-tail_of_file:]
    file_list = []
    for i, file_in in enumerate(file_in_dir):
        if file_in.endswith(ftype):
            file_list.append(file_in)
    return file_list

def main(INAPATH, TAG, fcopy, fsql, fforce, verbose):
    #

    import os,sys

    import numpy as np
    import cygno as cy
    
    import datetime
    
    connection = cy.daq_sql_cennection(verbose)
    if not connection:
        print ("ERROR: Sql connetion")
        sys.exit(1)
    print ("Checking file localy and remote: ", datetime.datetime.now().time())
    for i, file_in in enumerate(files_in_dir(INAPATH, ftype='mid.gz', tail_of_file=100, verbose=False)):
            #
            # loop on run*.gz files
            #
            run_number = int(file_in.split('run')[-1].split('.mid.gz')[0])
            
            if not fforce and cy.daq_read_runlog_replica_status(connection, run_number, storage="cloud", verbose=verbose)==1:
                    print ("File ", file_in, " ok, nothing done")
            else:
                if not os.path.exists(INAPATH+file_in.split(".")[0]+".mid"):
                    md5sum = cy.cmd.file_md5sum(INAPATH+file_in)
                    filesize = os.path.getsize(INAPATH+file_in)
                    if (verbose): 
                        print("Filename", file_in)
                        print("run_number", run_number)
                        print("MD5", md5sum)          
                        print("fsql", fsql)
                        print("fcopy", fcopy)
                    if (fsql): 
                        cy.daq_update_runlog_replica_status(connection, run_number, storage="local", status=1, verbose=verbose)
                        cy.daq_update_runlog_replica_checksum(connection, run_number, md5sum, verbose=verbose)
                        cy.daq_update_runlog_replica_size(connection, run_number, filesize, verbose=verbose)



                    remotesize = cy.s3.obj_size(file_in,tag=TAG, 
                                             bucket='cygno-data', session="infncloud-wlcg", 
                                             verbose=verbose)
                    if filesize >= 5400000000:
                        print ("WARNING: file too large to be copy", file_in, filesize)
                        if (fsql):
                            cy.daq_update_runlog_replica_status(connection, run_number, 
                                                                storage="cloud", status=2, verbose=verbose)
                    else:
                        if (filesize != remotesize and filesize>0):
                            print ("WARNING: file size mismatch", file_in, filesize, remotesize)
                            if (fcopy):
                                print (">>> coping file: "+file_in)
                                status, isthere = cy.s3.obj_put(INAPATH+file_in,tag=TAG, 
                                                             bucket='cygno-data', session="infncloud-wlcg", 
                                                             verbose=verbose)
                                if verbose: print (">>> status: ", status, "sql:", fsql)
                                if status and fsql:
                                    cy.daq_update_runlog_replica_status(connection, run_number, 
                                                                        storage="cloud", status=1, verbose=verbose)
                                    cy.daq_update_runlog_replica_tag(connection, run_number, TAG=TAG, verbose=verbose)
                                else:
                                    print ("ERROR: Copy on S3 faliure")
                        else:
                            print ("File ", file_in, " ok")
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
    max_tries   = 5

    parser = OptionParser(usage='usage: %prog [-t [{:s}] -i [{:s}]  -n [{:d}] rv]\n'.format(TAG,INAPATH, max_tries))
    parser.add_option('-i','--inpath', dest='inpath', type='string', default=INAPATH, help='PATH to raw data')
    parser.add_option('-t','--tag', dest='tag', type='string', default=TAG, help='tag where dir for data')
    parser.add_option('-c','--copy', dest='copy', action="store_true", default=False, help='upload data on S3 if error')
    parser.add_option('-q','--sql', dest='sql', action="store_true", default=False, help='update sql')
    parser.add_option('-f','--force', dest='force', action="store_true", default=False, help='force full recheck of data')
    parser.add_option('-v','--verbose', dest='verbose', action="store_true", default=False, help='verbose output')
    (options, args) = parser.parse_args()
    if options.verbose: 
        print ("opions", options)
        print ("args", args)
     
    main(options.inpath, options.tag, options.copy, options.sql, options.force, options.verbose)