"""
Ciao Giovanni,

per quanto riguarda il servizio docker compose, abbiamo una guida al seguente link (se per caso hai modo di guardarla, i tuoi feedback sarebbero utilizzati per migliorarla):

https://guides.cloud.infn.it/docs/users-guides/en/latest/users_guides/howto7.html

in particolare, per quanto riguarda le variabili d'ambiente, nel form di configurazione cliccando sul pulsante "add" è possibile aggiungere delle coppie chiave valore. La chiave è il nome della variabile che puoi usare nel docker-compose file nella forma ${NOME_VAR}. Quindi, nel caso di docker container mysql, se vuoi passare la password di root, puoi definire nel form la variabile MYSQL_ROOT_PASSWORD con il valore che deve assumere e nel docker compose file puoi richiamarla per esempio così:

db:
    container_name: db
    image: mysql:5.7
    restart: always
    environment:
      - MYSQL_ROOT_PASSWORD=${MYSQL_ROOT_PASSWORD}
      - ....

Questo perchè il sistema di orchestrazione crea in automatico nella dir del docker compose il file di environment .env con tutte le variabili che definisci da dashboard. In più trovi anche una variabile "interna" chiamata HOST_PUBLIC_IP che puoi utilizzare nel docker compose e che è avvalorata automaticamente con l'IP della VM (che non è noto a priori, ma viene scritto a runtime nel file .env)
"""

# SQL connection 
import os

MYSQL_ROOT_PASSWORD = '9754f510c12f8f1005cdb16dc51834c4'
MYSQL_DATABASE      = 'cygno_db'
MYSQL_USER          = 'cygno_producer'
MYSQL_PASSWORD      = 'e3b46beda9650197978b7b7e80464f73'
MYSQL_PORT          = 6033

myhost = os.uname()[1]
if (myhost=='cygno-daq-labe'): # LNF
    MYSQL_IP            = "131.154.96.215"
else:
    MYSQL_IP            = "131.154.96.221"


GF_SECURITY_ADMIN_USER = 'admin'
GF_SECURITY_ADMIN_PASSWORD = '9754f510c12f8f1005cdb16dc51834c4'


""" setup del token daq per la CLOUD. https://codimd.web.cern.ch/s/_XqFfF_7V

**** RICORDARSI che il token va chiesto solo per una macchina e poi copiate le chiavi qui stotto per le altre ****

export REFRESH_TOKEN="eyJhbGciOiJub25lIn0.eyJqdGkiOiIxMDU2NDFhZS0zODlhLTQ3NWYtYTgyYi1jN2FmNjk0NjE1YTcifQ."
export IAM_CLIENT_SECRET="APABvAtqWkRUH3GQfLiTJzBGiqFpOV7KMmdZtLOtxZgTo6QrvWYI-8ZAYAfHiavFst5jmuKQe-ffofr4Au0eJAg"
export IAM_CLIENT_ID="4b53b391-e7a0-42bb-be5d-a6109c1ae4c5"
export IAM_SERVER=https://iam.cloud.infn.it/
unset OIDC_SOCK; unset OIDCD_PID; eval `oidc-keychain`
oidc-gen --client-id $IAM_CLIENT_ID --client-secret $IAM_CLIENT_SECRET --rt $REFRESH_TOKEN --manual --issuer $IAM_SERVER --pw-cmd="echo pwd" --redirect-uri="edu.kit.data.oidc-agent:/redirect http://localhost:29135 http://localhost:8080 http://localhost:4242" --scope "openid email wlcg wlcg.groups profile offline_access" infncloud-wlcg

"""
