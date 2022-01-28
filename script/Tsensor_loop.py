#!/usr/bin/env python3
#
# G. Mazzitelli Febraury 2017
# Tool to Manage Files through the directory of data Acquired
# 
# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
def get_xml_url(url = "http://localhost:8082/values.xml"):
    import requests
    import xmltodict

    # url = "http://192.168.1.126/values.xml"
    # url = "http://localhost:8082/values.xml"
    response = requests.get(url)
    return xmltodict.parse(response.content)

def append_srt2file(file, data):
    hs = open(file,"a")
    hs.write(data+"\n")
    hs.close() 

def dump_Tsensor(url = "http://192.168.1.126/values.xml", file="Tsensor.log", update=60, verbose=False):
    import time
    init = True
    while True:
        data = get_xml_url(url)
        if init:
            value = "Time Date {} {} {} {}".format((data['root']['ch1']['name']).replace(' ', '_'), 
                                                   (data['root']['ch2']['name']).replace(' ', '_'), 
                                                   (data['root']['ch3']['name']).replace(' ', '_'), 
                                                   (data['root']['ch4']['name']).replace(' ', '_'))

            append_srt2file(file, value)
            init = False
            t0 = time.time()

        value = "{} {} {} {} {} {}".format(int(time.time()-t0), time.strftime('%Y%m%dT%H%M%S'),
                        data['root']['ch1']['aval'], 
                        data['root']['ch2']['aval'], 
                        data['root']['ch3']['aval'], 
                        data['root']['ch4']['aval'])
        append_srt2file(file, value)
        if verbose:
            print(value)
        time.sleep(update)


if __name__ == '__main__':
    from optparse import OptionParser
    import datetime
    
    now = datetime.datetime.now()
    fout = "Tsensor_"+now.strftime("%Y%m%d_%H%M")+".log"

    parser = OptionParser(usage='Tsenosr.py [OPTION1,..,OPTIONN]\n -u sensor ip [192.168.1.126]\n -f file name ['+fout+']\n -t [600]')
    parser.add_option('-u','--url', dest='url', type='string', default='192.168.1.126', help='sensor ip address;');
    parser.add_option('-f','--file', dest='file', type="string", default=fout, help='output file;');
    parser.add_option('-t','--uptime', dest='uptime', type='string', default='600', help='file uptime;');
    parser.add_option('-v','--verbose', dest='verbose', action="store_true", default=False, help='verbose print;');
    (options, args) = parser.parse_args()
    print (" T/P sensor at ip: {}\n log started on file: {}\n updated avery {} seconds".format(options.url, options.file, options.uptime))
    dump_Tsensor(url =  "http://"+options.url+"/values.xml", file= options.file, update= int(options.uptime), verbose=options.verbose)
