#!/bin/bash
# 0 22 * * * /root/dodas-docker-images/docker/CYGNO/tape/script/backup_sql.sh > /dev/null 2>&1
export SDIR="/var/lib/docker/volumes/grafana_dbdata/_data/"
export ODIR="/root/"
/usr/bin/tar -zcvf ${ODIR}grafana_`date +%Y%m%d`.tar.gz ${SDIR}
echo grafana_`date +%Y%m%d`.tar.gz >> ${ODIR}backup.dat
last=`tail -2 ${ODIR}backup.dat | head -1`
rm ${ODIR}$last
source /root/.bashrc
/usr/local/bin/cygno_repo put cygno-data ${ODIR}grafana_`date +%Y%m%d`.tar.gz -t BCK -s infncloud-wlcg
