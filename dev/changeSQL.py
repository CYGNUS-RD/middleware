import os
import stat

import mysql.connector
import cygno as cy
from cygno import cmd

def sql_update_reco_status(run,value,connection):
    cmd.update_sql_value(connection, table_name="Runlog", row_element="run_number", 
                     row_element_condition=run, 
                     colum_element="online_reco_status", value=value, 
                     verbose=False)
    

def main(verbose=True):
    
    connection = mysql.connector.connect(
      host="127.0.0.1",
      user=os.environ['MYSQL_USER'],
      password=os.environ['MYSQL_PASSWORD'],
      database=os.environ['MYSQL_DATABASE'],
      port=3306
    )

    sql_update_reco_status(16798,-1,connection)
    
if __name__ == "__main__":
    from optparse import OptionParser
    parser = OptionParser(usage='usage: %prog\t ')
    parser.add_option('-v','--verbose', dest='verbose', action="store_true", default=False, help='verbose output;');
    (options, args) = parser.parse_args()
    main(verbose=options.verbose)
