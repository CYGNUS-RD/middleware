#!/usr/bin/env python3
#
# G. Mazzitelli & S. Piacentini 2023
# script compressione midas file per DAQ LNGS/LNF
#

def storeStatus(filen, size, status, remotesize, outfile):
    from cygno import cmd
    stchar = ' '.join([filen, str(size), str(status), str(remotesize)])
    cmd.append2file(stchar, outfile)
    return stchar


def daq_sql_connection_local(verbose=False):
    import mysql.connector
    import os
    try:
        connection = mysql.connector.connect(
          host='localhost',
          user=os.environ['MYSQL_USER'],
          password=os.environ['MYSQL_PASSWORD'],
          database=os.environ['MYSQL_DATABASE'],
          port=3306
        )
        if verbose: print(connection)
        return connection
    except:
        return False


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
    from cygno import cmd

    #
    # deault parser value
    #
    TAG         = os.environ['TAG']
    INAPATH     = os.environ['INAPATH']# '/data01/data/'
    DAQPATH     = os.environ['DAQPATH']# '/home/standard/daq/'
    verbose=False


    client = midas.client.MidasClient("fileCompressor")

    compressing_files = 0
    compressing_runs = []

    connection = daq_sql_connection_local(verbose)#cy.daq_sql_cennection(verbose)
    if not connection:
        print('{:s} ERROR: Sql connetion'.format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        sys.exit(1)

    while True:
        try:
            # compress statment

#            file_in_dir=sorted(os.listdir(INAPATH))

            files = (
               entry for entry in os.scandir(INAPATH)
               if entry.is_file() and entry.name.startswith("run") and entry.name.endswith(".mid")
            )


            # Ordinamento per nome e prendo solo gli ultimi 100
            last_100 = sorted(files, key=lambda e: e.name)[-100:]

            file_in_dir = [f.name for f in last_100]

            try:

                for i in range(0, np.size(file_in_dir)):

                    runN = int(file_in_dir[i].split('run')[-1].split('.mid')[0])
                    connection = daq_sql_connection_local(verbose)
                    number_of_events=cmd.read_sql_value(connection, table_name="Runlog", row_element="run_number", 
                                       row_element_condition=str(runN), 
                                       colum_element="number_of_events", 
                                       verbose=False)
                    print(runN, number_of_events, file_in_dir)
                    if number_of_events==None: 
                        number_of_events=0 
                    if number_of_events>1 and not (runN in compressing_runs):
#                    if ('run' in str(file_in_dir[i]))   and \
#                    ('.mid' in str(file_in_dir[i]))  and \
#                    (not ('.gz' in str(file_in_dir[i]))) and \
#                    (not('.crc32c' in str(file_in_dir[i]))) and\
#                    ((str(file_in_dir[i]).split('.mid')[0] + '.crc32c') in file_in_dir) and \
#                    (not ( (str(file_in_dir[i]) + '.gz') in file_in_dir)) and \
#                    (not file_in_dir[i].startswith('.')):
                        if compressing_files < 8:
                            dtime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            print('{:s} Compressing file: {:s}'.format(dtime, file_in_dir[i]))
                            os.system('gzip ' + INAPATH + file_in_dir[i] +' &')
                            compressing_files += 1
                            compressing_runs.append(runN)
                            print(compressing_runs)
            except:
                print('{:s} ERROR: Compressing files'.format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            # upload statment

            found = False
            for i, runN in enumerate(compressing_runs):

                midfilename = INAPATH+"run"+str(runN)+".mid"
                if not os.path.isfile(midfilename):



#            for i in range(0, np.size(file_in_dir)):
#                if ('run' in str(file_in_dir[i]))   and \
#                ('.mid.gz' in str(file_in_dir[i]))  and \
#                (not (str(file_in_dir[i]).split('.gz')[0] in file_in_dir)) \
#                and (not file_in_dir[i].startswith('.')):

#                	runN = int(file_in_dir[i].split('run')[-1].split('.mid.gz')[0])

#                	if runN in compressing_runs:
                        dtime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        print('{:s} File successfully compressed: {:s}'.format(dtime, file_in_dir[i]))
                        compressing_runs.remove(runN)
                        # upadete sql with new file local status
                        cy.daq_update_runlog_replica_status(connection,runN, storage="local",status=1, verbose=verbose)
                        found = True
                        if compressing_files > 0:
                           compressing_files -= 1
 
            if not found:
                client.communicate(30)
                time.sleep(30)
            #print("Restarting loop...")

        except KeyboardInterrupt:
            client.deregister_event_request(buffer_handle, request_id)
            client.disconnect()
            print ("\nBye, bye...")
            sys.exit()


if __name__ == "__main__":
    main()
