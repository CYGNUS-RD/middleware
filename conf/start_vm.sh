#!/bin/bash
if [ "${VM_SERVICE}" = "sqlLNGS" ]; then
#   cd ./tape
#   docker compose up -d 
   cd ../mariadb
   docker compose  up -d 
# to restart only when running
#   cd ../analyzer
#   docker compose up -d 
elif [ "${VM_SERVICE}" = "GRAFANA" ]; then
   cd ./grafana
   docker compose up -d 
   cd ../mariadb
   docker compose --profile grafana up -d
#   docker compose -f docker-compose_lnf_mango.yaml up -d 
elif [ "${VM_SERVICE}" = "SENTINEL" ]; then
   cd ./sentinel
   docker compose up -d 
elif [ "${VM_SERVICE}" = "BACKEND" ]; then
   cd ./backend
   docker compose up -d
   cd ./web
   docker compose up -d
elif [ "${VM_SERVICE}" = "KAFKA" ]; then
   cd ./kafka
   docker compose up -d 
else
  echo "No VM services to be start"
fi
