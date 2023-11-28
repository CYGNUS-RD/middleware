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
    
def main(options):
    #
    max_tries   = options.tries
    verbose     = options.verbose
    SESSION     = options.session
    TAG         = options.tag
    bucket      = options.bucket
    INAPATH    = options.inpath
    start_copy  = options.start
    end_copy    = options.end
    estension  = options.estension
#    log = False
#    if options.log:
#        log = True
#        logfile = options.log

    while True:
        # loop on midas (ecape on midas events)
        try: 
            file_in_dir=os.listdir(INAPATH)
            nfile = len(file_in_dir)
            print ("Cheching file localy: ", datetime.datetime.now().time())
            print ("File in dir %d" % np.size(file_in_dir), start_copy, end_copy)
            for i in range(0, np.size(file_in_dir)):
                if ('run' in str(file_in_dir[i]))   and \
                (estension in str(file_in_dir[i]))  and \
                (not file_in_dir[i].startswith('.')):
                    #
                    # loop on run*.gz files
                    #
                    run_number = int(file_in_dir[i].split('run')[-1].split('.mid.gz')[0])
                    if run_number >=start_copy and run_number <=end_copy:
                        dtime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        
                        filesize = os.path.getsize(INAPATH+file_in_dir[i])
                        try:
                            if verbose :
                                print("Uploading: "+INAPATH+file_in_dir[i])
                                print(INAPATH+file_in_dir[i], TAG, bucket, SESSION, verbose, filesize)
                            if filesize < 5400000000: # ~ 5 GB
                                dtime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                print('{:s} Uploading file: {:s}'.format(dtime, file_in_dir[i]))
                                status, isthere = cy.s3.obj_put(INAPATH+file_in_dir[i],tag=TAG,
                                                                bucket=bucket, session=SESSION,
                                                                verbose=verbose)

                        except Exception as e:
                            print('{:s} ERROR file: {:s} --> '.format(dtime, file_in_dir[i]), e)
                            sys.exit(-1)

                        if verbose:
                            print('{:s} Upload done: {:s}'.format(dtime, file_in_dir[i]))
    
            time.sleep(10)


        except KeyboardInterrupt:
            print ("\nBye, bye...")
            sys.exit()

if __name__ == "__main__":

    from optparse import OptionParser
    import os,sys
    import datetime
    import numpy as np
    import cygno as cy
    import time
    import boto3
    from boto3sts import credentials as creds

    
    #
    # default parser value
    #
    TAG         = os.environ['TAG']
    INAPATH     = os.environ['INAPATH']
    SESSION     = "infncloud-wlcg"
    bucket      = "cygno-data"
    max_tries   = 5
    max_tail    = 10
    deepverb    = False
    
    start_copy  = 0
    end_copy    = 0

    parser = OptionParser(usage='usage: %prog [-t [{:s}] -i [{:s}]  -n [{:d}] rv]\n'.format(TAG, INAPATH, max_tries))
    parser.add_option('-t','--tag', dest='tag', type='string', default=TAG, help='tag where dir for data')
    parser.add_option('-b','--bucket', dest='bucket', type='string', default=bucket, help='cloud bucket to put data')
    parser.add_option('-i','--inpath', dest='inpath', type='string', default=INAPATH, help='PATH to raw data [./]')
    parser.add_option('-l','--log', dest='log', type='string', default='', help='log file ex /home/pippo/stored.log')
    parser.add_option('-n','--tries', dest='tries', type=int, default=max_tries, help='# of retry upload temptative')
    parser.add_option('-s','--session', dest='session', type='string', default=SESSION, help='session [infncloud-iam]')
    parser.add_option('-e','--estension', dest='estension', type='string', default='.mid.gz', help='estentions ex .trc')
    parser.add_option('-v','--verbose', dest='verbose', action="store_true", default=False, help='verbose output')
    
    parser.add_option(     '--start', dest='start', type=int, default=start_copy, help='first run to copy')
    parser.add_option(     '--end', dest='end', type=int, default=end_copy, help='last run to copy')

    (options, args) = parser.parse_args()

    newupoload = []
    print('{:s} mac2cloud started'.format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
#    session = creds.assumed_session(SESSION, endpoint="https://minio.cloud.infn.it/", verify=True)
#    s3 = session.client('s3', endpoint_url="https://minio.cloud.infn.it/", config=boto3.session.Config(signature_version='s3v4'),
#                                                verify=True)

    main(options)
