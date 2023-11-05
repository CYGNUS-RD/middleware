#!/usr/bin/env python3
#
# G. Mazzitelli 2022
# versione DAQ LNGS/LNF per midas reco2sql 
# cheker and sql update Aug 23 
#
import mysql.connector
import pandas as pd
import numpy as np
import uproot
import os
connection = mysql.connector.connect(
  host=os.environ['MYSQL_IP'],
  user=os.environ['MYSQL_USER'],
  password=os.environ['MYSQL_PASSWORD'],
  database=os.environ['MYSQL_DATABASE'],
  port=int(os.environ['MYSQL_PORT'])
)
sql = "SELECT * FROM `Runlog`  WHERE `online_reco_status` = 1 ORDER BY `run_number` DESC LIMIT 1;"
sql_table = pd.read_sql(sql, connection)
run_number = value.run_number[0]
tf = uproot.open("https://s3.cloud.infn.it/v1/AUTH_2ebf769785574195bde2ff418deac08a/cygno-analysis/RECO/Winter23/reco_run{:5d}_3D.root".format(run_number))
print(run_number)
#tf = uproot.open("https://s3.cloud.infn.it/v1/AUTH_2ebf769785574195bde2ff418deac08a/cygno-analysis/RECO/Winter23/reco_run23035_3D.root")
#sc_integral = tf["Events;1/sc_integral"].array(library="np")
#run = tf["Events;1/run"].array(library="np")
tf["Events;1"].show()