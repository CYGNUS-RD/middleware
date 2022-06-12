#!/usr/bin/env python3
#
# G. Mazzitelli 2022
# versione DAQ LNGS/LNF per midas file2cloud
#

def main():
    #
    from optparse import OptionParser
    import os,sys
    import datetime
    import numpy as np
    import os,sys
    from cygno import s3, his, cmd
    import time
    import midas
    import midas.client
    
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
    max_uploed_cicle = 5 #number of maximun upload per cycle
    
    client = midas.client.MidasClient("midas2cloud")
    
    while True:
        try:
            file_in_dir=sorted(os.listdir(INAPATH))
            print ("Start DAQ backup at: ", datetime.datetime.now().time())
            print ("File in dir %d" % np.size(file_in_dir))
            
            ipload = 1 # index of file uploaded
            for i in range(0, np.size(file_in_dir)):
                if ('run' in str(file_in_dir[i])) and \
                ('.mid.gz' in str(file_in_dir[i])) and (not file_in_dir[i].startswith('.') and (ipload<=max_uploed_cicle)):

                    runN = int(file_in_dir[i].split('run')[-1].split('.mid.gz')[0])
                    if verbose : 
                        print("---------------------- Upload:", ipload)
                        print(file_in_dir[i], runN)
                        print(STOROUT)       

                    if cmd.grep_file(file_in_dir[i], STOROUT) == "":
                        print('Transferring file: '+file_in_dir[i])
                        current_try = 0
                        status, isthere = False, False # flag to know if to go to next run
                        while(not status):   #tries many times for errors of connection or others that may be worth another try
                            if verbose : 
                                print("Uploading: "+INAPATH+file_in_dir[i])
                                print(INAPATH+file_in_dir[i],TAG, 'cygno-data', "infncloud-wlcg", verbose)
                            status, isthere = s3.obj_put(INAPATH+file_in_dir[i],tag=TAG, bucket='cygno-data', session="infncloud-wlcg", verbose=verbose)

                            # status, isthere = True, True

                            if status:
                                if isthere:
                                    cmd.append2file(file_in_dir[i], STOROUT)
                                    newupoload.append(file_in_dir[i])
                            else:
                                current_try = current_try+1
                                if current_try==max_tries:
                                    print('ERROR: Max try number reached: '+str(current_try))
                                    status=True
                        ipload+=1
                    else:
                        print ("WARNING: >>>> No file uploaded")      

            if to != '':
                when = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                subject = "latest news fro DAQ!"
                if len(newupoload)>0:
                    body = 'last files uploaded at '+when+': '+str([s for s in newupoload])
                    # allert_mail(subject, body, to, verbose)
                else:
                    body = 'WARNING: no new uploaded files at '+when
                    allert_mail(subject, body, to, verbose)
            print("\n Finished!!")
            client.communicate(10)
            time.sleep(10)
        except KeyboardInterrupt:
            client.deregister_event_request(buffer_handle, request_id)
            client.disconnect()
            print ("\nBye, bye...")
            sys.exit()


if __name__ == "__main__":
    main()