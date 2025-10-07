#!/bin/bash

if [ -z "$1" ]; then
  echo "plese enter list filename filelist_20250425 whitout exetetion TXT"
  exit 1
fi

name="$1"
flog="../../web/apache/html/log.log"
fall=`wc ${name}.txt`
touch ${name}.log

IFS=$'\n';
for line in $(cat ${name}.txt); do 
    fdone=`grep ok ${name}.log | wc`
    s1=`echo $fdone | awk '{print $1}'`
    s2=`echo $fall | awk '{print $1}'`
    perc=$(awk "BEGIN { printf \"%.2f\", 100 * $s1 / $s2 }")
    date > $flog 
    tail -1 ${name}.log >> ${flog} 
    echo "status: $s1 files done over $s2, $perc%" >> ${flog}

    while true; do
        ./cp_minio2ba.py ${line}
        if [ $? -eq 0 ]; then
            break
        else
            echo "ERROR: ${line} Retiring..." >> ${name}.log
        fi
    done
done >> ${name}.log

