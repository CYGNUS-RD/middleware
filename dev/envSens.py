#!/bin/python3
#import serial
import time # Optional (required if using time.sleep() below)
import numpy as np
import pandas as pd
import sys
import mysql.connector
import os
import midas
import midas.client

def read_density(filename='/home/user/Scaricati/density.csv'):
    
    import subprocess
    command = 'tail -1 '+filename+' && echo "" > '+filename
    status, output = subprocess.getstatusoutput(command)
    if status==0:
        try:
            dtmp = output.split(',')
            data = "{:.3f} {:.3f}".format(float(dtmp[2])-273.15, float(dtmp[3]))
        except:
            print("ERROR: density meter")
            data = "-1 -1"
    else:
        data = "-1 -1"
    return data

def get_xml_url(url = "http://localhost:8082/values.xml"):
    import requests
    import xmltodict
    try:
        response = requests.get(url)
        return xmltodict.parse(response.content)
    except Exception as e:
        print("ERROR:", e)
        return False

def append_srt2file(file, data):
    try:
        hs = open(file,"a")
        hs.write(data+"\n")
        hs.close() 
    except:
        print("ERROR writing file")
        sys.exit(3)
    return

def dump_Tsensor(url = "192.168.1.126", verbose=False):
    import time
    
    # colums=['T_room [C]', 'H_room [%]', 'D_room [C]', 'P_room [hP]']

    urladd = "http://"+url+"/values.xml"  
    try:
        data = get_xml_url(urladd)

        value = "{} {} {} {}".format(
                        data['root']['ch1']['aval'], 
                        data['root']['ch2']['aval'], 
                        data['root']['ch3']['aval'], 
                        data['root']['ch4']['aval'])
        if "Error" in value:
            value = "-1 -1 -1 -1"
    except:
        print("ERROR reading Tsensor device")
        value = "-1 -1 -1 -1"
    return value


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

def main(update, fileout, sql, url, verbose):

    urlxml = "http://"+url+"/values.xml"
    connection = mysql.connector.connect(
          host='localhost',
          user=os.environ['MYSQL_USER'],
          password=os.environ['MYSQL_PASSWORD'],
          database=os.environ['MYSQL_DATABASE'],
          port=3306
    )
    client = midas.client.MidasClient("envSens")
    table_name = "envSens"
    start=time.time()

    try:
        while (True):
            data_2_save = {}
            data_2_save['epoch']=int(time.time())
            try:
                # env = dump_Tsensor(url, verbose)
                data = get_xml_url(urlxml)
                if verbose: print("DATA:", data)
                data_2_save['T']=float(data['root']['ch1']['aval'])
                data_2_save['H']=float(data['root']['ch2']['aval'])
                data_2_save['D']=float(data['root']['ch3']['aval'])
                data_2_save['P']=float(data['root']['ch4']['aval'])
                df = pd.DataFrame(data_2_save, index=[0])
                df.replace(np.nan, -99, inplace=True)
                if verbose: print(data_2_save)
                if sql: push_panda_table_sql(connection,table_name, df)
            except Exception as e: 
                print("ERROR:", e)
            client.communicate(10)
            time.sleep(update)
            
    except KeyboardInterrupt:
        print('Bye!')
        client.disconnect()
        sys.exit(0)

if __name__ == '__main__':
    from optparse import OptionParser
    import datetime

    now = datetime.datetime.now()
    fout = "data_sensors_"+now.strftime("%Y%m%d_%H%M")+".log"

    parser = OptionParser(usage='Tsenosr.py ')
    parser.add_option('-u','--url', dest='url', type='string', default='192.168.1.126', help='sensor ip address;');
    parser.add_option('-f','--fileout', dest='fileout', type="string", default=fout, help='output file;');
    parser.add_option('-t','--uptime', dest='uptime', type='string', default='600', help='file uptime;');
    parser.add_option('-s','--sql', dest='sql', action="store_true", default=False, help='dump on sql;');
    parser.add_option('-v','--verbose', dest='verbose', action="store_true", default=False, help='verbose print;');
    (options, args) = parser.parse_args()
    print (" T/P sensor at ip: {}\n log started on file: {}\n updated avery {} seconds".format(options.url, options.fileout, options.uptime))
    if options.fileout == fout:
        txt_columns='unix date hour P_in_[hP] H_in_[%] T_in_[C] P_out_[hP] H_out_[%] T_out_[C] T_room_[C] H_room_[%] D_room_[C] P_room_[hP] CF4'
        append_srt2file(options.fileout, txt_columns)
    main(update=int(options.uptime), fileout= options.fileout, sql = options.sql, url = options.url, verbose=options.verbose)
