#!/usr/bin/env python3

import sys
import os
import time
import midas
import midas.client
import ctypes
from matplotlib import pyplot as plt

def debug_get(client):
    c_path = ctypes.create_string_buffer(b"/")
    hKey = ctypes.c_int()
    client.lib.c_db_find_key(client.hDB, 0, c_path, ctypes.byref(hKey))

    buf = ctypes.c_char_p()
    bufsize = ctypes.c_int()
    bufend = ctypes.c_int()

    client.lib.c_db_copy_json_save(client.hDB, hKey, ctypes.byref(buf), ctypes.byref(bufsize), ctypes.byref(bufend))

    print("-" * 80)
    print("FULL DUMP")
    print("-" * 80)
    print(buf.value)
    print("-" * 80)
    print("Chars 17000-18000")
    print("-" * 80)
    print(buf.value[17000:18000])
    print("-" * 80)

    as_dict = midas.safe_to_json(buf.value, use_ordered_dict=True)

    client.lib.c_free(buf)

    return as_dict

def main(verbose=False):
    client = midas.client.MidasClient("middleware")
    buffer_handle = client.open_event_buffer("SYSTEM",None,1000000000)
    request_id = client.register_event_request(buffer_handle, sampling_type = 2)

    fpath = os.path.dirname(os.path.realpath(sys.argv[0]))

    while True:
        # odb = client.odb_get("/")
        odb = debug_get(client)

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
