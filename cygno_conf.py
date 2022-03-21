# SQL connection 


import os

MYSQL_ROOT_PASSWORD = '9754f510c12f8f1005cdb16dc51834c4'
MYSQL_DATABASE      = 'cygno_db'
MYSQL_USER          = 'cygno_producer'
MYSQL_PASSWORD      = 'e3b46beda9650197978b7b7e80464f73'
MYSQL_PORT          = 6033
myhost = os.uname()[1]
if (myhost=='cygno-daq-labe'): # LNF
    MYSQL_IP            = "131.154.96.215"
else:
    MYSQL_IP            = "131.154.96.221"


GF_SECURITY_ADMIN_USER = 'admin'
GF_SECURITY_ADMIN_PASSWORD = '9754f510c12f8f1005cdb16dc51834c4'
