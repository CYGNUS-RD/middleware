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
import cygno as cy
import time
import datetime

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
    except Exception as e:
        print('ERROR >>> SQL insert {}'.format(e))
        return 1

    
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

def get_s3_client(client_id, client_secret, endpoint_url, session_token):
    # Specify the session token, access key, and secret key received from the STS
    import boto3
    sts_client = boto3.client('sts',
            endpoint_url = endpoint_url,
            region_name  = ''
            )

    response_sts = sts_client.assume_role_with_web_identity(
            RoleArn          = "arn:aws:iam:::role/S3AccessIAM200",
            RoleSessionName  = 'cygno',
            DurationSeconds  = 3600,
            WebIdentityToken = session_token # qua ci va il token IAM
            )

    s3 = boto3.client('s3',
            aws_access_key_id     = response_sts['Credentials']['AccessKeyId'],
            aws_secret_access_key = response_sts['Credentials']['SecretAccessKey'],
            aws_session_token     = response_sts['Credentials']['SessionToken'],
            endpoint_url          = endpoint_url,
            region_name           = '')
    return s3

def upload_file_2_S3(file_name, client_id, client_secret,  endpoint_url, bucket, tag, tfile, verbose=False):

    with open(tfile) as file:
        token = file.readline().strip('\n')
    session_token= token
    if (verbose): print("TOKEN > ",tfile, token)
    s3 = get_s3_client(client_id, client_secret, endpoint_url, session_token)
    filename = file_name.split('/')[-1]
    try:
        s3.upload_file(file_name, Bucket=bucket, Key=tag+'/'+filename)
        return 0
    except Exception as e:
        print('ERROR S3 file update: {:s} --> '.format(file_name), e)
        return 1

def Gauss3(x, a0, x0, s0):
    import numpy as np
    return a0 * np.exp(-(x - x0)**2 / (2 * s0**2))

def plt_hist(data, run,  xmin=4000, xmax=16000, bins=60, verbose=False):
    import matplotlib.pyplot as plt
    import base64
    from json import dump
    import numpy as np
    import seaborn as sns
    from scipy.optimize import curve_fit
    sns.set()


    stat = data[(data>xmin) & (data<xmax)].mean(), data[(data>xmin) & (data<xmax)].std()
    fig,ax = plt.subplots()

    y,x = np.histogram(data, range=(xmin,xmax), bins = bins)
    x=x[:-1]
    w = abs(x[1] - x[0])
    xfmin=stat[0]-0.6*stat[1]/(stat[0]/12000)
    xfmax=stat[0]+3*stat[1]

    popt, pcov = curve_fit(Gauss3,x[(x>xfmin) & (x<xfmax)], y[(x>xfmin) & (x<xfmax)], 
                           p0=[500, stat[0], stat[1]])
    perr = np.sqrt(np.diag(pcov))

    ax.bar(x,y, width=w, label='run{}\nmean: {:.1f}\nstd: {:.1f}'.format(run,stat[0], stat[1]))
    ax.plot(x[(x>xfmin) & (x<xfmax)], Gauss3(x[(x>xfmin) & (x<xfmax)], *popt), 'r--', 
            label='p0 = {:.1f}+/-{:.1f}\np1 = {:.1f}+/-{:.1f}\np3 = {:.1f}+/-{:.1f}'\
            .format(popt[0],perr[0],popt[1],perr[1],popt[2],perr[2]))


    ax.legend()
    plt.savefig('/tmp/fe.png')
    if verbose: plt.show()
    with open('/tmp/fe.png', 'rb') as f:
        img_bytes = f.read()
    f.close()
    img_base64 = base64.b64encode(img_bytes).decode('utf-8')
    if verbose: print(img_base64)

    del fig, ax, data
    return img_base64, stat, popt, perr

def update_sql_value(connection, table_name, column_element, value, verbose=False):
    if isinstance(value, str):
        svalue="\""+value+"\""
    else:
        svalue=str(value)
    sql = "UPDATE `"+table_name+"` SET `"+column_element+"` = "+svalue+" WHERE 1;"
    if verbose: print(sql)
    try:
        mycursor = connection.cursor()
        mycursor.execute(sql)
        connection.commit()
        if verbose: print(mycursor.rowcount, "Update done")
        mycursor.close()
        return 0
    except Exception as e:
        print('ERROR >>> SQL update {}'.format(e))
        return 1

def alpha_rate(cut,length, xmax=40):
#    cut = dfall.sc_integral/dfall.sc_nhits
    nalpha = 0
    for i in range(len(cut)):
#        nalpha +=len(cut[i][(cut[i]>40) & (dfall.sc_length[i]>50)])
        nalpha +=len(cut[i][(cut[i]>40) & (length[i]>50)])
    return nalpha

def push_update_panda_table_sql(connection, table_name, df, verbose=False):

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
            sql = "INSERT INTO `"+table_name+"` (`" +cols + "`) VALUES (" + "%s,"*(len(row)-1) + "%s) " \
            "ON DUPLICATE KEY UPDATE "+", ".join(["`"+s+"`='"+str(df[s].values[0])+"'" for s in df.columns])
            if verbose: print(sql)
            mycursor.execute(sql, tuple(row.astype(str)))
            connection.commit()

        mycursor.close()
        return 0 
    except Exception as e:
        print('SQL ERROR --> ', e)
        return 1

def sql2df(url="http://lnf.infn.it/~mazzitel/php/cygno_sql_query.php?site=lnf&db=gm_data", verbose=False):
    import requests
    r = requests.get(url, verify=False)
    df = pd.read_json(url)
    return df

def self_updete_history(connection, verbose=False):
    dv = sql2df(url="http://lnf.infn.it/~mazzitel/php/cygno_sql_query.php?db=tmpTable")
    img_base64, popt, perr = scan_plt(dv)
    if img_base64:
       update_sql_value(connection, "tmpTable", "image_scan_fe", img_base64, verbose)
    dv = dv.iloc[:, : 10] 
    dv['data']=datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d')
    dv['par0']=popt[0]
    dv['par1']=popt[1]
    if not (push_update_panda_table_sql(connection, 'tmpTableHist', dv)):
       print("history updated")
    else:
       print("ERROR in history updated")

def scan_fit(x, a, b):
    import numpy as np
    return a * (1 - np.exp(-(x + 142.26) / (-0.02 * a + 19897.75) )) * np.exp(-x / b)

def scan_plt(dv, verbose=False):
    import matplotlib.pyplot as plt
    import base64
    from json import dump
    import numpy as np
    import seaborn as sns
    from scipy.optimize import curve_fit
    import datetime
    
    sns.set()
    try:
        fig,ax = plt.subplots(figsize=(10,5))
        x = [50.0, 150.0, 250.0, 350.0, 465.0]
        y = [dv.peak_fe_1.values[0], dv.peak_fe_2.values[0], dv.peak_fe_3.values[0], 
             dv.peak_fe_4.values[0], dv.peak_fe_5.values[0]]
        label = datetime.datetime.fromtimestamp(dv.epoch_fe_3).strftime('%Y-%m-%d')

        ax.plot(x,y, 'b.-', label=label)
        ax.legend()
        x1 = np.linspace(0,500, 100)
        popt, pcov = curve_fit(scan_fit,x,y, p0=[450000, 700])
        perr = np.sqrt(np.diag(pcov))
        y1 = scan_fit(x1, *popt)
        ax.plot(x1,y1, 'r--', label='a={:.2e}, b={:.2e}'.format(popt[0], popt[1]))
        ax.legend()

        ax.set_xlim(0,500)
        plt.savefig('/tmp/fe.png')
        if verbose: plt.show()
        with open('/tmp/fe.png', 'rb') as f:
            img_bytes = f.read()
        f.close()
        img_base64 = base64.b64encode(img_bytes).decode('utf-8')
        if verbose: print(img_base64)
        del fig, ax
        return img_base64, popt, perr
    except Exception as e:
        print('ERROR scan fit error {}'.format(e))
        return False, [0,0], [0,0]

def main(verbose=False):
    import os
    import cygno as cy
    connection = mysql.connector.connect(
          host=os.environ['MYSQL_IP'],
          user=os.environ['MYSQL_USER'],
          password=os.environ['MYSQL_PASSWORD'],
          database=os.environ['MYSQL_DATABASE'],
          port=int(os.environ['MYSQL_PORT'])
    )

    client_id     = os.environ['IAM_CLIENT_ID']
    client_secret = os.environ['IAM_CLIENT_SECRET']
    endpoint_url  = os.environ['ENDPOINT_URL']

    bucket        = 'cygno-analysis'
    tag           = 'pkl'
    tfile         = '/tmp/token'
    SPARK         = 1.0e7 # 2*100*2304**2+9*1e6

    reco_path0 = os.environ['RECO_PATH']
    sql_limit = os.environ['SQL_LIMIT']
    force_rebuild = os.environ['FORCE_REBUILD']

    BASE_URL = 'https://s3.cloud.infn.it/v1/AUTH_2ebf769785574195bde2ff418deac08a/'
    reco_path = BASE_URL+'cygno-analysis/RECO/'+reco_path0
    sqlLog = "SELECT * FROM `Runlog`  WHERE `online_reco_status` = 1 AND `pedestal_run` = 0 ORDER BY `run_number` DESC LIMIT "+str(sql_limit)+";"
    sqlRec = "SELECT * FROM `SlowReco` ORDER BY `run_mean` DESC;"
    sql_Log = pd.read_sql(sqlLog, connection)
    try:
        sql_Rec = pd.read_sql(sqlRec, connection)
    except:
        sql_Rec = pd.DataFrame(columns = ['run_mean'])
        sql_Rec.loc[0] = 0
    for i, run in enumerate(sql_Log.run_number):
        if verbose: print(run, force_rebuild==1, not (run in sql_Rec.run_mean.astype(int).tolist()), sql_Rec.run_mean.astype(int).tolist())
        if force_rebuild==1 or not (run in sql_Rec.run_mean.astype(int).tolist()):
#        if not (run in sql_Rec.run_mean.astype(int).tolist()):
            if (sql_Log[sql_Log.run_number==run].source_type.values[0]==1):
                source1 = sql_Log[sql_Log.run_number==run].source_position.values[0]==3.5
                source2 = sql_Log[sql_Log.run_number==run].source_position.values[0]==10.5
                source3 = sql_Log[sql_Log.run_number==run].source_position.values[0]==17.5
                source4 = sql_Log[sql_Log.run_number==run].source_position.values[0]==24.5
                source5 = sql_Log[sql_Log.run_number==run].source_position.values[0]==32.5
            else:
                source1 = False
                source2 = False
                source3 = False
                source4 = False
                source5 = False

            print("analyzing run: ",run, str(sql_Log[sql_Log.run_number==run].run_description.values), source1, source2, source3, source4, source5)
            try:
                file_out_name="/tmp/"+"reco_run{0:05d}_3D.pkl.gz".format(run)
                branch_data = {}
                slow_data = {}
                file_url = reco_path+"reco_run{:5d}_3D.root".format(run)
                tf = uproot.open(file_url)
                names = tf["Events;1"].keys()

                for i, name in enumerate(names):
                    var = tf["Events;1/"+name].array(library="np")

                    if var[0].ndim == 0:
                        branch_data[name] = np.hstack(var)
                        slow_data[name+"_mean"]=var.mean()
                        if name == "run":
                           slow_data[name+"_epoch"]=start2epoch(sql_Log, run)
                        else:
                           slow_data[name+"_std"]=var.std() 

                    else:
                        branch_data[name] = var

                val_LY = GetLY(tf)
                slow_data["LY_mean"]=val_LY[0]
                slow_data["LY_std"]=val_LY[1]

                if source1:  
                   img64,stat1, popt1, perr1 = plt_hist(np.hstack(np.array(branch_data["sc_integral"])), run, xmin=4000, xmax=16000, bins=60, verbose=verbose)
                   update_sql_value(connection, "tmpTable", "image_fe_1", img64, verbose)
                   update_sql_value(connection, "tmpTable", "peak_fe_1", popt1[1], verbose)
                   update_sql_value(connection, "tmpTable", "epoch_fe_1", start2epoch(sql_Log, run), verbose)
                   self_updete_history(connection)
                if source2:  
                   img64,stat2, popt2, perr2 = plt_hist(np.hstack(np.array(branch_data["sc_integral"])), run, xmin=4000, xmax=16000, bins=60, verbose=verbose)
                   update_sql_value(connection, "tmpTable", "image_fe_2", img64, verbose)
                   update_sql_value(connection, "tmpTable", "peak_fe_2", popt2[1], verbose)
                   update_sql_value(connection, "tmpTable", "epoch_fe_2", start2epoch(sql_Log, run), verbose)
                   self_updete_history(connection)
                if source3:  #and (reco_path0.split('/')[0]=='Run4'):
                   img64,stat3, popt3, perr3 = plt_hist(np.hstack(np.array(branch_data["sc_integral"])), run, xmin=4000, xmax=16000, bins=60, verbose=verbose)
                   update_sql_value(connection, "tmpTable", "image_fe_3", img64, verbose)
                   update_sql_value(connection, "tmpTable", "peak_fe_3", popt3[1], verbose)
                   update_sql_value(connection, "tmpTable", "epoch_fe_3", start2epoch(sql_Log, run), verbose)
                   self_updete_history(connection)
                else:
                   stat3 = (0.0,0.0)
                   popt3 = (0.0,0.0,0.0)
                if source4:  
                   img64,stat4, popt4, perr4 = plt_hist(np.hstack(np.array(branch_data["sc_integral"])), run, xmin=4000, xmax=16000, bins=60, verbose=verbose)
                   update_sql_value(connection, "tmpTable", "image_fe_4", img64, verbose)
                   update_sql_value(connection, "tmpTable", "peak_fe_4", popt4[1], verbose)
                   update_sql_value(connection, "tmpTable", "epoch_fe_4", start2epoch(sql_Log, run), verbose)
                   self_updete_history(connection)
                if source5:  
                   img64,stat5, popt5, perr5 = plt_hist(np.hstack(np.array(branch_data["sc_integral"])), run, xmin=4000, xmax=16000, bins=60, verbose=verbose)
                   update_sql_value(connection, "tmpTable", "image_fe_5", img64, verbose)
                   update_sql_value(connection, "tmpTable", "peak_fe_5", popt5[1], verbose)
                   update_sql_value(connection, "tmpTable", "epoch_fe_5", start2epoch(sql_Log, run), verbose)
                   self_updete_history(connection)
                slow_data["Fe_mean"]=stat3[0]
                slow_data["Fe_fit"]=popt3[1]

                spark = len(np.array(branch_data["cmos_integral"])[np.array(branch_data["cmos_integral"])>SPARK])
                slow_data["spark"]=spark
                slow_data["alpha"]=alpha_rate(np.array(branch_data["sc_integral"])/np.array(branch_data["sc_nhits"]),np.array(branch_data["sc_length"]), xmax=40)
                slow_data["reco_tag"]=reco_path0.split('/')[0]
                print(slow_data)

                df = pd.DataFrame(slow_data, index=[0]) # qui index=0 perche sono scalari
                df.replace(np.nan, -99, inplace=True)

                table_name = "SlowReco"
                push_panda_table_sql(connection,table_name, df)
                df_all = pd.DataFrame(branch_data)
                df_all.to_pickle(file_out_name, compression={'method': 'gzip', 'compresslevel': 1})
                upload_file_2_S3(file_out_name, client_id, client_secret,  endpoint_url, bucket, tag, tfile, verbose=verbose)
                cy.cmd.rm_file(file_out_name)
# ############## Update Params
                parma_data = {}
                parma_data['run']=branch_data['run'][0]
                parma_data['run_epoch']=start2epoch(sql_Log, run)
                names = tf["Reco_params;1"].keys()
                for i, name in enumerate(names):
                    var = tf["Reco_params;1/"+name].array(library="np")
                    parma_data[name]=var
                parma_data['hash']=tf["gitHash;1"].member('fTitle')
                dp = pd.DataFrame(parma_data)
                push_panda_table_sql(connection,'SlowRecoParams', dp)
# ############## Update History
#                tn = datetime.datetime.fromtimestamp(time.time()).strftime('%H')
#                if tn=='23':
#                    dv = sql2df(url="http://lnf.infn.it/~mazzitel/php/cygno_sql_query.php?db=tmpTable")
#                    dh = sql2df(url="http://lnf.infn.it/~mazzitel/php/cygno_sql_query.php?db=tmpTableHist")
#                    tv = datetime.datetime.fromtimestamp(dv.epoch_fe_3).strftime('%Y-%m-%d')
#                    th = datetime.datetime.fromtimestamp(dh.iloc[-1].epoch_fe_3).strftime('%Y-%m-%d')
#                    if not tv==th:
#                       if not (push_update_panda_table_sql(connection, 'tmpTableHist', dv.iloc[:, : 10])):
#                           print("history updated")
#                       else:
#                           print("ERROR in history updated")

            except Exception as e:
                print('ERROR >>> {}'.format(e))
                continue
    print("DONE")
main()
