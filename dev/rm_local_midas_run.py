#!/usr/bin/env python3
#
# G. Mazzitelli 2022
# versione DAQ LNGS/LNF per midas file2cloud 
# cheker and sql update Nov 22 
#

def main(INAPATH, fforce, start, end, verbose):
    #

    import os,sys

    import numpy as np
    import cygno as cy
    
    import datetime
    
    connection = cy.daq_sql_cennection(verbose)
    if not connection:
        print ("ERROR: Sql connetion")
        sys.exit(1)
            
    file_in_dir=sorted(os.listdir(INAPATH))
    print ("Cheching file localy and remote: ", datetime.datetime.now().time())
    print ("File in dir %d" % np.size(file_in_dir), start, end)
    for i in range(0, np.size(file_in_dir)):
        if ('run' in str(file_in_dir[i]))   and \
        ('.mid.gz' in str(file_in_dir[i]))  and \
        (not file_in_dir[i].startswith('.')):
            #
            # loop on run*.gz files
            #
            run_number = int(file_in_dir[i].split('run')[-1].split('.mid.gz')[0])
            if run_number >=start and run_number <=end:
                if cy.daq_read_runlog_replica_status(connection, run_number, storage="cloud", verbose=verbose)==1 and \
                cy.daq_read_runlog_replica_status(connection, run_number, storage="tape", verbose=verbose)==1:
                    print ("Removing file: ", file_in_dir[i])
                    if fforce:
                        command = '/bin/rm -f '+ INAPATH+file_in_dir[i]
                    else:
                        command = '/bin/rm -i '+ INAPATH+file_in_dir[i]
                    os.system(command)
                    cy.cmd.append2file(file_in_dir[i], LOGFILE)
                    if cy.daq_update_runlog_replica_status(connection, run_number, storage="local", status=0, verbose=verbose):
                        print ("ERROR: updateting sql db for file", file_in_dir[i])
                        sys.exit(1)
                    else:
                        print ("Update replica ok", file_in_dir[i])
                else:
                    print ("ERROR: no file in sql DB", file_in_dir[i])
                    sys.exit(1)
#             else:
#                 print ("WARNING: not in selected range: ", file_in_dir[i] , start, end)

#     cy.daq_update_runlog_replica_status(connection, run_number, storage="local", status=1, verbose=verbose)
#     cy.daq_update_runlog_replica_checksum(connection, run_number, md5sum, verbose=verbose)
#     cy.daq_update_runlog_replica_size(connection, run_number, filesize, verbose=verbose)


                
    sys.exit(0)
if __name__ == "__main__":
    from optparse import OptionParser
    #
    # deault parser value
    #
    import datetime
    now = datetime.datetime.now()

    TAG         = 'LNGS'
    INAPATH     = '/data01/data/'
    LOGFILE     = '/home/standard/daq/online/log/rm_{:d}{:d}{:d}.log'.format(now.year, now.month, now.day)
    max_tries   = 5

    parser = OptionParser(usage='usage: %prog [-t [{:s}] -i [{:s}]  -n [{:d}] rv]\n'.format(TAG,INAPATH, max_tries))
    parser.add_option('-i','--inpath', dest='inpath', type='string', default=INAPATH, help='PATH to raw data')
    parser.add_option('-s','--start', dest='start', type='string', default=INAPATH, help='start file numeber [ex 512]')
    parser.add_option('-e','--end', dest='end', type='string', default=INAPATH, help='end file numeber [ex 1512]')
    parser.add_option('-f','--force', dest='force', action="store_true", default=False, help='force full recheck of data')
    parser.add_option('-v','--verbose', dest='verbose', action="store_true", default=False, help='verbose output')
    (options, args) = parser.parse_args()
    if options.verbose: 
        print ("opions", options)
        print ("args", args)
    if options.start.isnumeric():
        start= int(options.start)
    else:
        start=0
    if options.end.isnumeric():
        end= int(options.end)
    else:
        end=100000000000
    main(options.inpath, options.force, start, end, options.verbose)