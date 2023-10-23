#!/bin/sh
# 0 22 * * * /root/dodas-docker-images/docker/CYGNO/tape/script/backup_sql.sh > /dev/null 2>&1
export SDIR="/var/lib/docker/volumes/sql_dbdata/_data/"
export ODIR="/root/"
/usr/bin/tar -zcvf ${ODIR}sql_`date +%Y%m%d`.tar.gz ${SDIR}
echo sql_`date +%Y%m%d`.tar.gz >> ${ODIR}backup.dat
last=`tail -2 ${ODIR}backup.dat | head -1`
rm ${ODIR}$last
