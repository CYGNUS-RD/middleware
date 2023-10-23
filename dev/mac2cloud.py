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
    
def main():
    #
    from optparse import OptionParser
    import os,sys
    import datetime
    import numpy as np
    import cygno as cy
    import time
    import boto3
    from boto3sts import credentials as creds

    
    #
    # deault parser value
    #
    TAG         = "WC"
    INAPATH     = "./"
    SESSION     = "infncloud-iam"
    bucket      = "cygno-data"
    max_tries   = 5
    max_tail    = 10
    deepverb    = False

    parser = OptionParser(usage='usage: %prog [-t [{:s}] -i [{:s}]  -n [{:d}] rv]\n'.format(TAG, INAPATH, max_tries))
    parser.add_option('-t','--tag', dest='tag', type='string', default=TAG, help='tag where dir for data')
    parser.add_option('-i','--inpath', dest='inpath', type='string', default=INAPATH, help='PATH to raw data [./]')
    parser.add_option('-l','--log', dest='log', type='string', default='', help='log file ex /home/pippo/stored.log')
    parser.add_option('-n','--tries', dest='tries', type=int, default=max_tries, help='# of retry upload temptative')
    parser.add_option('-s','--session', dest='session', type='string', default=SESSION, help='session [infncloud-iam]')
    parser.add_option('-e','--estension', dest='estension', type='string', default='', help='estentions ex .trc')
    parser.add_option('-v','--verbose', dest='verbose', action="store_true", default=False, help='verbose output')
    (options, args) = parser.parse_args()


    max_tries   = options.tries
    verbose     = options.verbose
    SESSION     = options.session
     
    INAPATH    = options.inpath

    estension  = options.estension
    log = False
    if options.log:
        log = True
        logfile = options.log
        

    newupoload = []
    print('{:s} mac2cloud started'.format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    session = creds.assumed_session(SESSION, endpoint="https://minio.cloud.infn.it/", verify=True)
    s3 = session.client('s3', endpoint_url="https://minio.cloud.infn.it/", config=boto3.session.Config(signature_version='s3v4'),
                                                verify=True)
    
    while True:
        # loop on midas (ecape on midas events)
        try: 
            file_in_dir=os.listdir(INAPATH)
            nfile = len(file_in_dir)
            for i in range(0, np.size(file_in_dir)): 
                if (not file_in_dir[i].startswith('.')) \
                and (estension in str(file_in_dir[i])):
                    dtime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    if verbose:              
                        print('{:s} Transferring file {:s} {:d}'.format(dtime, file_in_dir[i], nfile-i))

                    if verbose and deepverb: 
                        print(INAPATH+file_in_dir[i],TAG, bucket, session, verbose)
                    try:
                        s3.upload_file(INAPATH+file_in_dir[i], Bucket=bucket, Key=TAG+'/'+file_in_dir[i])
                    except Exception as e:
                        print('{:s} ERROR file: {:s} --> '.format(dtime, file_in_dir[i]), e)
                        sys.exit(-1)

                    cy.cmd.rm_file(INAPATH+file_in_dir[i])
                    if log:
                        cy.cmd.append2file(file_in_dir[i], logfile)
                    if verbose and deepverb:              
                        print('{:s} file removed: {:s}'.format(dtime, file_in_dir[i]))

                        ##############################
                    if verbose and deepverb: 
                        print('{:s} Upload done: {:s}'.format(dtime, file_in_dir[i]))

            time.sleep(10)


        except KeyboardInterrupt:
            print ("\nBye, bye...")
            sys.exit()

if __name__ == "__main__":
    main()
