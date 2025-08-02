#!/usr/bin/env python3
#
# G. Mazzitelli 2022
# versione DAQ LNGS/LNF per midas file2cloud
#
# RUCIO upload
#

def storeStatus(filen, size, status, result, outfile):
    from cygno import cmd
    stchar = ' '.join([filen, str(size), str(status), str(result)])
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
    import subprocess
    #
    # deault parser value
    #
    version  ='s3v4'

    BARI = 1
    session  ='infncloud-wlcg'
    bucket   = 'cygno-data'
    
    TAG         = os.environ['TAG']
    INAPATH     = os.environ['INAPATH']# '/data01/data/'
    DAQPATH     = os.environ['DAQPATH']# '/home/standard/daq/'
    max_tries   = 5
    #to = 'giovanni.mazzitelli@lnf.infn.it, davide.pinci@roma1.infn.it, francesco.renga@roma1.infn.it'
    to = ''

    parser = OptionParser(usage='usage: %prog [-t [{:s}] -i [{:s}]  -d [{:s}] -n [{:d}] -b [{:d}] rv]\n'.format(TAG, INAPATH,DAQPATH, max_tries,BARI))
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
    tag         = options.tag
     
    INAPATH    = options.inpath
    DAQPATH    = options.daqpath

    STOROUT    = DAQPATH+"online/log/daq_stored.log"
    FILELOK    = INAPATH+"analized.lok"
    newupoload = []
    print('{:s} midas2cloud started'.format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    
    client = midas.client.MidasClient("midas2cloud")
    
    compressing_files = 0
    
    key = tag+'/'

    
    GB = 1024 ** 3
    config = TransferConfig(multipart_threshold=5*GB)

    
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
            except:
                print('{:s} ERROR: Compressing files'.format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                
            # upload statment
            for i, filename in enumerate(file_in_dir):
                # questo if va sostituito con il check sul DB ABANDONADO IL LISI SUL FILE CHE E' LENTO
                if ('run' in str(filename))   and \
                ('.mid.gz' in str(filename))  and \
                (not (str(filename).split('.gz')[0] in file_in_dir)) \
                and (not filename.startswith('.')):
                    
                    runN = int(filename.split('run')[-1].split('.mid.gz')[0])
                    
                    if cy.cmd.grep_file(filename, STOROUT) == "" or \
                    cy.daq_read_runlog_replica_status(connection, runN, storage="local", verbose=verbose)==0: 
                        
                        dtime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        
                        print('{:s} Udatentig matadata for filer file: {:s}'.format(dtime, filename))
                        
                        filesize = os.path.getsize(INAPATH+filename)               
                        md5sum = cy.cmd.file_md5sum(INAPATH+filename)

                        # upadete sql with new file local status
                        cy.daq_update_runlog_replica_status(connection, 
                                                            runN, storage="local", 
                                                            status=1, verbose=verbose)
                        cy.daq_update_runlog_replica_checksum(connection, runN, 
                                                              md5sum, verbose=verbose)
                        cy.daq_update_runlog_replica_size(connection, runN, 
                                                              filesize, verbose=verbose)

                        dtime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        print('{:s} Transferring file: {:s}'.format(dtime, filename))
                        if compressing_files > 0:
                            compressing_files -= 1
                        current_try = 0
                        status = False 
                        while(not status):   
                            if verbose: print(INAPATH+filename,tag, bucket, session, verbose, filesize)
                            if filesize < 5400000000: # ~ 5 GB
                                dtime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                print('{:s} Uploading file: {:s}'.format(dtime, filename))
                                try:
                                   # remeber config sile in /home/.rucio.cfg
#                                   docker run --rm -v /home/.rucio.cfg:/home/.rucio.cfg -v INAPATH+filename:/app/filename rucio-uploader \
#                                   --file ./filename --bucket bucket --did_name key+filename --upload_rse CNAF_USERDISK --transfer_rse T1_USERTAPE --account rucio-daq
                                   docker_command = [ "docker", "run", "--rm",
                                                      "-v", "/home/.rucio.cfg:/home/.rucio.cfg",
                                                      "-v", INAPATH+filename+":/app/"+filename,
                                                      "rucio-uploader",  # nome dell'immagine Docker
                                                      "--file", filename,
                                                      "--bucket", bucket,
                                                      "--did_name", key+filename,
                                                      "--upload_rse", "CNAF_USERDISK",
                                                      "--transfer_rse", "T1_USERTAPE",
                                                      "--account", "rucio-daq"
                                                      ]
                                   if verbose: print(docker_command)
                                   result = subprocess.run(docker_command, capture_output=True, text=True)
#                                    s3.upload_file(INAPATH+filename, Bucket=bucket, Key=key+filename,Config=config)
#                                    response=s3.head_object(Bucket=bucket,Key=key+filename)
#                                    remotesize = int(response['ContentLength'])
                                    newupoload.append(storeStatus(filename, filesize, status, 
                                                                      result.stderr, STOROUT))
                                    cy.daq_update_runlog_replica_status(connection, 
                                                                            runN, storage="cloud", 
                                                                            status=1, verbose=verbose)
                                    cy.daq_update_runlog_replica_tag(connection, runN, 
                                                                         TAG=tag, verbose=verbose)

                                    print('{:s} Upload done: {:s}'.format(dtime, filename))
                                    status = True
                                    
                                except Exception as e:
                                    current_try = current_try+1
                                    print('{:s} ERROR: Uploading file: {:s}'.format(dtime, filename))
                                    print(e)
                                    if current_try==max_tries:
                                        print('ERROR: Max try number reached: '+str(current_try))
                                        status = True
                            else:
                                storeStatus(filename, filesize, status, 0,  STOROUT)
                                print('{:s} ERROR: File too large, not uploaded: {:s}'.format(dtime,filename))
                                status=True                                      
                                      
                
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
