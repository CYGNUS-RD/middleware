#!/bin/bash
if [ "${VM_SERVICE}" = "sqlLNGS" ]; then
   cd ./tape
   docker compose up -d 
   cd ../mariadb
   docker compose up -d 
   cd ../analyzer
   docker compose up -d 
elif [ "${VM_SERVICE}" = "GRAFANA" ]; then
   cd ./grafana
   docker compose up -d 
   cd ../mariadb
   docker compose up -d 
elif [ "${VM_SERVICE}" = "SENTINEL" ]; then
   cd ./sentinel
   docker compose up -d 
else
  echo "No VM services to be start"
fi
