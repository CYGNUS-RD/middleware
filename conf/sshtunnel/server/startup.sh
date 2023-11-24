#!/bin/bash
i=0
env
d=`date +%Y-%M-%d\ %H:%M:%S`

echo "$d STARTNG reverse BASTION-->"

adduser -D ${BASTION_USER}
echo "${BASTION_USER}:${BASTION_PASWD}" | chpasswd
chown -R ${BASTION_USER} /home/${BASTION_USER}/.ssh
chgrp -R ${BASTION_USER} /home/${BASTION_USER}/.ssh

# Start SSH service
/usr/sbin/sshd -D
