#!/bin/bash
i=0
env
WAIT=86400
# SDIR="/var/lib/docker/volumes/sql_dbdata/_data/"
# ODIR="/root/"
if [ -z "$TOKEN_FILE" ]; then 
	TOKEN_FILE='/tmp/token'  
else 
	echo "using ${TOKEN_FILE}"
fi
if [ -z "$BCK_START_NAME" ]; then 
	BCK_START_NAME='file'  
else 
	echo "using ${BCK_START_NAME}"
fi

echo "STARTNG BACKUPPER-->"
while :
do
	d=`date +%Y-%M-%d\ %H:%M:%S`
    echo "$d backupping date $i"
    file=${BCK_START_NAME}_`date +%Y%m%d`.tar.gz
    /bin/tar -zcvf /root/$file /root/data/
    /opt/file2s3_fromHTTPtoken.py /root/$file ${IAM_CLIENT_ID} ${IAM_CLIENT_SECRET} -f ${TOKEN_FILE}
    if [ $? -ne 0 ]; then 
        echo "ERROR: no file copied"
    else
        rm /root/$file
        echo "BACKUP DONE"
    fi
	i=$((i+1))
	sleep $WAIT
done
