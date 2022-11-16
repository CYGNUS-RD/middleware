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
    import os,sys
    from cygno import s3, his, cmd
    import time
    
    #
    # deault parser value
    #
    TAG         = 'LNGS'
    INAPATH     = '/data01/data/'
    DAQPATH     = '/home/standard/daq/'
    max_tries   = 5
    #to = 'giovanni.mazzitelli@lnf.infn.it, davide.pinci@roma1.infn.it, francesco.renga@roma1.infn.it'
    to = ''

    parser = OptionParser(usage='usage: %prog [-t [{:s}] -i [{:s}]  -d [{:s}] -n [{:d}] rv]\n'.format(TAG,INAPATH,DAQPATH, max_tries))
    parser.add_option('-t','--tag', dest='tag', type='string', default=TAG, help='tag where dir for data')
    parser.add_option('-i','--inpath', dest='inpath', type='string', default=INAPATH, help='PATH to raw data')
    parser.add_option('-d','--daqpath', dest='daqpath', type='string', default=DAQPATH, help='DAQ to raw data')
    parser.add_option('-v','--verbose', dest='verbose', action="store_true", default=False, help='verbose output')
    (options, args) = parser.parse_args()

    verbose    = options.verbose
    INAPATH    = options.inpath
    DAQPATH    = options.daqpath

    STOROUT    = DAQPATH+"online/daq_stored.log"
    
    file_in_dir=sorted(os.listdir(INAPATH))
    print ("Cheching file localy and remote: ", datetime.datetime.now().time())
    print ("File in dir %d" % np.size(file_in_dir))
    for i in range(0, np.size(file_in_dir)):
        if ('run' in str(file_in_dir[i]))   and \
        ('.mid.gz' in str(file_in_dir[i]))  and \
        (not file_in_dir[i].startswith('.')):
            filesize = os.path.getsize(INAPATH+file_in_dir[i])
            remotesize = s3.obj_size(file_in_dir[i],tag=TAG, 
                                     bucket='cygno-data', session="infncloud-wlcg", 
                                     verbose=verbose)
            if (filesize != remotesize and remotesize>0 and filesize < 5400000000):
                print ("WARNING: file size mismatch", file_in_dir[i], filesize, remotesize)
                status, isthere = s3.obj_put(INAPATH+file_in_dir[i],tag=TAG, 
                                             bucket='cygno-data', session="infncloud-wlcg", 
                                             verbose=verbose)
            else:
                print ("File ", file_in_dir[i], " ok")
                
                
if __name__ == "__main__":
    main()