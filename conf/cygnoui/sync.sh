#!/bin/sh

# Definir variáveis
SERVER2="${SERVER2}"
SOURCE_DIR="${SOURCE_DIR}"
DEST_DIR="${DEST_DIR}"

# Executar rsync
rsync -avz -e "ssh -F /root/.ssh/config" --rsync-path="sudo rsync" ${SERVER2}:${SOURCE_DIR} ${DEST_DIR}
