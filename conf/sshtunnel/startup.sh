#!/bin/bash
i=0
env
d=`date +%Y-%M-%d\ %H:%M:%S`

echo "$d STARTNG reverse SSHTUNNEL-->"
chmod 600 /id_rsa
# cat /id_rsa
ssh -o StrictHostKeyChecking=no -vnNTR ${REMOTE_PORT}:${LOCAL_APP_NAME}:${LOCAL_PORT} ${USER}@${REMOTE_IP} -i /id_rsa
