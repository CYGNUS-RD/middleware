#!/usr/bin/env python3
#
# G. Mazzitelli 2022
# versione DAQ LNGS/LNF per midas reco2sql 
# cheker and sql update Aug 23 
#
import numpy as np
import uproot
import pandas as pd
import mysql.connector
import os

def push_panda_table_sql(connection, table_name, df):
    try:
        mycursor=connection.cursor()
        mycursor.execute("SHOW TABLES LIKE '"+table_name+"'")
        result = mycursor.fetchone()
        if not result:
            cols = "`,`".join([str(i) for i in df.columns.tolist()])
            db_to_crete = "CREATE TABLE `"+table_name+"` ("+' '.join(["`"+x+"` REAL," for x in df.columns.tolist()])[:-1]+")"
            print ("[Table {:s} created into SQL Server]".format(table_name))
            mycursor = connection.cursor()
            mycursor.execute(db_to_crete)

        cols = "`,`".join([str(i) for i in df.columns.tolist()])

        for i,row in df.iterrows():
            sql = "INSERT INTO `"+table_name+"` (`" +cols + "`) VALUES (" + "%s,"*(len(row)-1) + "%s)"
            mycursor.execute(sql, tuple(row.astype(str)))
            connection.commit()

        mycursor.close()
        return 0 
    except:
        return -1
    
def GetLY(tf):
    df_A = tf['Events'].arrays(['sc_rms', 'sc_tgausssigma', 'sc_width', 'sc_length', 'sc_xmean', 'sc_ymean', 'sc_integral'], library = 'pd')


    sel   = df_A[(df_A['sc_rms'] > 6)&
                 (0.152 * df_A['sc_tgausssigma'] > 0.5) &
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

def start2epoch(sql_Log, run):
    from datetime import datetime
    date = str(sql_Log[sql_Log.run_number==run].start_time.values[0])
    utc_time = datetime.strptime(date, "%Y-%m-%dT%H:%M:%S.000000000")
    epoch_time = (utc_time - datetime(1970, 1, 1)).total_seconds()
    return epoch_time


def main(verbose=False):
    connection = mysql.connector.connect(
          host=os.environ['MYSQL_IP'],
          user=os.environ['MYSQL_USER'],
          password=os.environ['MYSQL_PASSWORD'],
          database=os.environ['MYSQL_DATABASE'],
          port=int(os.environ['MYSQL_PORT'])
    )
    
    sqlLog = "SELECT * FROM `Runlog`  WHERE `online_reco_status` = 1 AND `pedestal_run` = 0 ORDER BY `run_number` DESC LIMIT 100;"
    sqlRec = "SELECT * FROM `SlowReco` ORDER BY `run_mean` DESC  LIMIT 100;"
    sql_Log = pd.read_sql(sqlLog, connection)
    try:
        sql_Rec = pd.read_sql(sqlRec, connection)
    except:
        sql_Rec = pd.DataFrame(columns = ['run_mean'])
        sql_Rec.loc[0] = 0
    for i, run in enumerate(sql_Log.run_number):
        if not (run in sql_Rec.run_mean.astype(int).tolist()):
            try:
                file_url = "https://s3.cloud.infn.it/v1/AUTH_2ebf769785574195bde2ff418deac08a/cygno-analysis/RECO/Winter23/reco_run{:5d}_3D.root".format(run)
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
                           values.append(start2epoch(sql_Log, run))
                        else:
                           columns.append(name+"_std")
                           values.append(var.std())
                val_LY = GetLY(tf)
                columns.append("LY_mean")
                values.append(val_LY[0])
                columns.append("LY_std")
                values.append(val_LY[1])
                print(values)
                df = pd.DataFrame(columns = columns)
                df.loc[0] = values
                table_name = "SlowReco"
                push_panda_table_sql(connection,table_name, df)
            except Exception as e:
                print('ERROR >>> {}'.format(e))
                continue
    print("DONE")
main()
