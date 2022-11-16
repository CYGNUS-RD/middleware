#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
import midas.file_reader
import sys
if sys.argv[1] == "":
    print ("<filename>")
else:
    try:
        filename = sys.argv[1]
        f = midas.file_reader.MidasFile(filename)
        print ("Open file: ", filename)
    except:
        print ("File name error: ", filename)
    #f = midas.file_reader.MidasFile('/jupyter-workspace/cloud-storage/cygno-data/LNGS/run01386.mid.gz')
    nev = 0
    for event in f:
        nev+=1
        if nev%10 == 0:
            print("read: ", nev)
            # event.dump()
