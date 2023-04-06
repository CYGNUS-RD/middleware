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

    STOROUT    = DAQPATH+"online/log/daq_stored.log"
    FILELOK    = INAPATH+"analized.lok"
    newupoload = []
    print('{:s} midas2cloud started'.format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
#    max_uploed_cicle = 1 # number of maximun upload per cycle
    
    client = midas.client.MidasClient("midas2cloud")
    
    compressing_files = 0
    
    connection_remote = cy.daq_sql_cennection(verbose)
    if not connection_remote:
        print('{:s} ERROR: Sql connetion'.format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        sys.exit(1)
    
    connection = daq_sql_connection_local(verbose)#cy.daq_sql_cennection(verbose)
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
                    
                    runN = int(file_in_dir[i].split('run')[-1].split('.mid.gz')[0])
                    
                    if cy.cmd.grep_file(file_in_dir[i], STOROUT) == "" or \
                    cy.daq_read_runlog_replica_status(connection, runN, storage="local", verbose=verbose)==0: 
                        # cy.cmd.grep_file(file_in_dir[i], STOROUT) == "" or 
                        
                        dtime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        
                        print('{:s} Udatentig matadata for filer file: {:s}'.format(dtime, file_in_dir[i]))
                        filesize = os.path.getsize(INAPATH+file_in_dir[i])               

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
                            #try:
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

                                            ###### Update SQL Remote
                                            
                                            #lastrun = cy.read_sql_value(connection, "Runlog", "run_number", 
                                            #   str(runN), "*",verbose)
                                            n_try = 3
                                            
                                            while (n_try>0):
                                            
                                                status_replica = replica_sql_value(connection, connection_remote, 
                                                                              "Runlog", "run_number",  str(runN),
                                                                              verbose=verbose)
                                                if status_replica:
                                                    break
                                                print("WARNING: SQL Replica try", n_try)
                                                n_try-=1
                                                connection_remote = cy.daq_sql_cennection(verbose)
                                                if not connection_remote:
                                                    print('{:s} ERROR: Sql connetion'\
                                                          .format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                                                    sys.exit(1)
                                                    
                                                    
                                            if n_try == 0: 
                                                print('ERROR: Max SQL try replica reached')
                                            else:
                                                print('{:s} Replica sql updated'.format(dtime) )
                                            
                                            
                                            
                                            
                                            ##############################
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
#                             except:
#                                 dtime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#                                 print('{:s} ERROR: Tranfering files: {:s}'.format(dtime,file_in_dir[i]))
                                      
                                      
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
