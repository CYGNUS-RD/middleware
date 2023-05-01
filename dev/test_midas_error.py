#!/usr/bin/env python3
#
# I. Abritta and G. Mazzitelli March 2022
# Middelware online recostruction 
# Modify by ... in date ...
#

import os, sys


def main(verbose=False):
    #from matplotlib import pyplot as plt

    import time

    import midas
    import midas.client

    
    client = midas.client.MidasClient("middleware")
    buffer_handle = client.open_event_buffer("SYSTEM",None,1000000000)
    request_id = client.register_event_request(buffer_handle, sampling_type = 2) 
    
    fpath = os.path.dirname(os.path.realpath(sys.argv[0]))
    
    
    while True:
        # 
        odb = client.odb_get("/")
        if verbose:
            print(odb)
        start1 = time.time()
              
        client.communicate(10)
        time.sleep(1)
        

    client.deregister_event_request(buffer_handle, request_id)

    client.disconnect()
    
        
if __name__ == "__main__":
    from optparse import OptionParser
    parser = OptionParser(usage='usage: %prog\t ')
    parser.add_option('-v','--verbose', dest='verbose', action="store_true", default=False, help='verbose output;');
    (options, args) = parser.parse_args()
    main(verbose=options.verbose)
