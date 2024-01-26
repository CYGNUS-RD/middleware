#!/usr/bin/env python3
#
# G. Mazzitelli 2023
# versione DAQ LNGS/LNF remouve file from cloud 
# cheker and sql update Dec. 23 
#

def main(tag, fforce, start, end, session, verbose):
    #

    import os,sys

    import numpy as np
    import cygno as cy
    import pandas as pd
    
    import datetime
    
    connection = cy.daq_sql_cennection(verbose)
    if not connection:
        print ("ERROR: Sql connetion")
        sys.exit(1)
    if verbose: print ("fatching db...")
    df = cy.read_cygno_logbook()
    run_numbers=df.run_number.values
    print ("Cheching file localy and remote: ", datetime.datetime.now().time())
    print ("File in dir %d" % np.size(run_numbers), start, end)
    for i, run_number in enumerate(run_numbers):
            if run_number >=int(start) and run_number <=int(end):
                if cy.daq_read_runlog_replica_status(connection, run_number, storage="cloud", verbose=verbose)==1 and \
                cy.daq_read_runlog_replica_status(connection, run_number, storage="tape", verbose=verbose)==1:
                    filename = 'run{:05d}.mid.gz'.format(run_number)
                    print ("removing run from cloud: ",run_number, filename)
                    if fforce:
                        delete = True
                    elif input("are you sure to delete {:} [y/n] ".format(filename)).lower() in ('y','yes', 'Y', 'YES'): 
                        delete = True
                    else:
                        delete = False
                    if delete:
                        cy.s3.obj_rm(filename, tag, bucket='cygno-data', session=session, verbose=verbose)
                        cy.cmd.append2file(filename, LOGFILE)
                        if cy.daq_update_runlog_replica_status(connection, run_number, storage="cloud", status=2, verbose=verbose):
                            print ("ERROR: updateting sql db for file", filename)
                            sys.exit(1)
                        else:
                            print ("Update replica ok", filename)
                else:
                    print ("ERROR: no run {:} in cloud/tape sql DB, jump to next".format(run_number))
    sys.exit(0)
if __name__ == "__main__":
    from optparse import OptionParser
    #
    # deault parser value
    #
    import datetime
    now = datetime.datetime.now()

    TAG         = 'LNGS'
    SESSION     = "infncloud-wlcg"
    START       = 0
    END         = 100000000000
    LOGFILE     = '/home/standard/daq/online/log/rm_cloud_{:d}{:d}{:d}.log'.format(now.year, now.month, now.day)
    max_tries   = 5

    parser = OptionParser(usage='usage: %prog -tsefnv')
    parser.add_option('-t','--tag', dest='tag', type='string', default=TAG, help='tag [{:}]'.format(TAG))
    parser.add_option('-s','--start', dest='start', type='string', default=START, help='start file number [ex 512]')
    parser.add_option('-e','--end', dest='end', type='string', default=END, help='end file number [ex 1512]')
    parser.add_option('-f','--force', dest='force', action="store_true", default=False, help='force')
    parser.add_option('-n','--session', dest='session', type='string', default=SESSION, help='session [{:}]'.format(SESSION))
    parser.add_option('-v','--verbose', dest='verbose', action="store_true", default=False, help='verbose output')
    (options, args) = parser.parse_args()
    if options.verbose: 
        print ("opions", options)
        print ("args", args)
    main(options.tag, options.force, options.start, options.end, options.session, options.verbose)
