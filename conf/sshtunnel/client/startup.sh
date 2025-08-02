#!/bin/bash
i=0
env
d=`date +%Y-%M-%d\ %H:%M:%S`

echo "$d STARTNG reverse SSHTUNNEL-->"
chmod 600 /root/.ssh/id_rsa
# cat /id_rsa
ssh -o StrictHostKeyChecking=no -vnNTC -L 0.0.0.0:${LOCAL_PORT}:${REMOTE_APP_NAME}:${REMOTE_PORT} ${USER}@${REMOTE_IP} -i /root/.ssh/id_rsa
