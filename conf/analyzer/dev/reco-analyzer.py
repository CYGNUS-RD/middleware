#!/usr/bin/env python3
#
# G. Mazzitelli 2022
# versione DAQ LNGS/LNF per midas reco-analyzer
#
import numpy as np
import uproot
import pandas as pd
import os

    
def GetLY(tf, verbose):
    df_A = tf['Events'].arrays(['sc_rms', 'sc_tgausssigma', 'sc_width', 'sc_length', 'sc_xmean',
                                'sc_ymean','sc_integral'], library = 'pd')

    if verbose: print (df_A)
    sel   = df_A[
        (df_A['sc_rms'] > 6) & (0.152 * df_A['sc_tgausssigma'] > 0.5) & 
        (np.sqrt((df_A['sc_xmean']-2304/2)**2 + (df_A['sc_ymean']-2304/2)**2) < 800)  & 
        (df_A['sc_integral'] > 30_000) & (df_A['sc_integral']<300_000)
    ].copy()

    p = np.array([7.51266058e-02, -1.32492111e+03])

    return p[0]*np.mean(sel['sc_integral'])+p[1], p[0]*np.std(sel['sc_integral']) / np.sqrt(len(sel))

def get_epoch(file_url):
    import requests
    from datetime import datetime
    r = requests.get(file_url)
    utc_time = datetime.strptime(r.headers['last-modified'], "%a, %d %b %Y %H:%M:%S %Z")
    epoch_time = (utc_time - datetime(1970, 1, 1)).total_seconds()
    return epoch_time


def main(start_run, verbose=False):
    import cygno as cy
    BASE_URL = 'https://s3.cloud.infn.it/v1/AUTH_2ebf769785574195bde2ff418deac08a/'
    try:
        runInfo=cy.read_cygno_logbook(sql=True,verbose=verbose)
        if verbose: print(runInfo)
    except Exception as e:
        print('ERROR >>> {}'.format(e))
    for i, run in enumerate(runInfo[runInfo.run_number>=start_run].run_number):
        if (runInfo[runInfo.run_number==run].online_reco_status.values[0]==1):
            print("analyzing run: ",run)
#            try:
            file_url = BASE_URL+'cygno-analysis/RECO/Winter23/reco_run{:5d}_3D.root'.format(run)
            tf = uproot.open(file_url)
            names = tf["Events;1"].keys()
            values = []
            columns = []
            for i, name in enumerate(names):
                var = tf["Events;1/"+name].array(library="np")
                if var[0].ndim == 0:
                    # print(i, name, var.mean(), var.std())
                    columns.append(name+"_mean")
                    values.append(var.mean())
                    if columns[-1]=='run_mean':
                       columns.append(name+"_epoch")
                       values.append(get_epoch(file_url))
                    else:
                       columns.append(name+"_std")
                       values.append(var.std())
            val_LY = GetLY(tf, verbose)
            columns.append("LY_mean")
            values.append(val_LY[0])
            columns.append("LY_std")
            values.append(val_LY[1])
            print(values)
            df = pd.DataFrame(columns = columns)
            df.loc[0] = values
            # except Exception as e:
            #     print('ERROR >>> {}'.format(e))
            #     continue
    print("DONE")
    exit(0)
if __name__ == "__main__":
    from optparse import OptionParser
    #
    # deault parser value
    #

    parser = OptionParser(usage='usage: %prog -r -v')
    parser.add_option('-r','--run', dest='run', type="string", default='-1', help='start run for rechek')
    parser.add_option('-v','--verbose', dest='verbose', action="store_true", default=False, help='verbose output')
    (options, args) = parser.parse_args()
    if options.verbose: 
        print ("options", options)
        print ("args", args)
    # if len(args)<1:
    #     parser.print_help()
    #     exit(1)
    main(int(options.run), options.verbose)

