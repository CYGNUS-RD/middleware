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

def replica_sql_value(connection, connection_remote, table_name, row_element, row_element_condition, verbose=False):
    import datetime
    sql = "SELECT * FROM `"+table_name+"` WHERE `"+row_element+"` = "+row_element_condition+";"
    #SELECT * FROM `Runlog` WHERE `run_number` = 1024;
    if verbose: print(sql)
    #try:
    # read from local
    mycursor = connection.cursor()
    mycursor.execute(sql)
    row = mycursor.fetchone()

    row_list = []

    for i,data in enumerate(row):
        if isinstance(data, datetime.datetime):
            data = data.strftime('%Y-%m-%d %H:%M:%S')
        row_list.append(data)
    row = tuple(row_list)

    cols = mycursor.column_names

    cols = "`,`".join([str(i) for i in list(cols)])

    mycursor.close()
    #except:
    #    return 0    
    #sql = "INSERT INTO `{}` (`" +cols+ "`) VALUES {}".format(table_name, row)
    sql = "INSERT INTO `"+table_name+"` (`" +cols+ "`) VALUES "+str(row)
    if verbose: print(sql)
    try:
        # replica on remote
        mycursor = connection_remote.cursor()
        #sql = "INSERT INTO `"+table_name+"` (`" +cols + "`) VALUES (" + "%s,"*(len(row)-1) + "%s)"
        mycursor.execute(sql)
        #mycursor.execute(sql, row.astype(str))
        connection_remote.commit()
        mycursor.close()
        
        if verbose: print(mycursor.rowcount, "Update done")

        return row[0]
    except:
        return 0

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
    
    #
    # deault parser value
    #
    TAG         = os.environ['TAG']
    INAPATH     = os.environ['INAPATH']# '/data01/data/'
    DAQPATH     = os.environ['DAQPATH']# '/home/standard/daq/'

    #parser = OptionParser(usage='usage: %prog [-t [{:s}] -i [{:s}]  -d [{:s}] -n [{:d}] rv]\n'.format(TAG, INAPATH,DAQPATH, max_tries))
    #parser.add_option('-t','--tag', dest='tag', type='string', default=TAG, help='tag where dir for data')
    #parser.add_option('-i','--inpath', dest='inpath', type='string', default=INAPATH, help='PATH to raw data')
    #parser.add_option('-d','--daqpath', dest='daqpath', type='string', default=DAQPATH, help='DAQ to raw data')
    #parser.add_option('-n','--tries', dest='tries', type=int, default=max_tries, help='# of retry upload temptative')
    #parser.add_option('-v','--verbose', dest='verbose', action="store_true", default=False, help='verbose output')
    #parser.add_option('-m','--mail', dest='mail', type='string', default=to, help='mail allert')
    #(options, args) = parser.parse_args()


    #max_tries   = options.tries
    #verbose     = options.verbose
    #to          = options.mail
     
    #INAPATH    = options.inpath
    #DAQPATH    = options.daqpath

    client = midas.client.MidasClient("fileCompressor")
    
    compressing_files = 0
    compressing_runs = np.array([])
    
    while True:
        try: 
            # compress statment
            file_in_dir=sorted(os.listdir(INAPATH))
            try:
				
                for i in range(0, np.size(file_in_dir)):
                    if ('run' in str(file_in_dir[i]))   and \
                    ('.mid' in str(file_in_dir[i]))  and \
                    (not ('.gz' in str(file_in_dir[i]))) and \
                    (not('.crc32c' in str(file_in_dir[i]))) and\
                    ((str(file_in_dir[i]).split('.mid')[0] + '.crc32c') in file_in_dir) and \
                    (not ( (str(file_in_dir[i]) + '.gz') in file_in_dir)) and \
                    (not file_in_dir[i].startswith('.')):
                        if compressing_files < 8:
                            dtime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            print('{:s} Compressing file: {:s}'.format(dtime, file_in_dir[i]))
                            os.system('gzip ' + INAPATH + file_in_dir[i] +' &')
                            compressing_files += 1
                            compressing_runs = np.append(compressing_runs, int(file_in_dir[i].split('run')[-1].split('.mid')[0]))
            except:
                print('{:s} ERROR: Compressing files'.format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            # upload statment
            
            found = False
            for i in range(0, np.size(file_in_dir)):
                if ('run' in str(file_in_dir[i]))   and \
                ('.mid.gz' in str(file_in_dir[i]))  and \
                (not (str(file_in_dir[i]).split('.gz')[0] in file_in_dir)) \
                and (not file_in_dir[i].startswith('.')):
                
                	runN = int(file_in_dir[i].split('run')[-1].split('.mid.gz')[0])
                	
                	if runN in compressing_runs:
                		dtime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                		print('{:s} File successfully compressed: {:s}'.format(dtime, file_in_dir[i]))
                		compressing_runs = compressing_runs[compressing_runs != runN]
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
