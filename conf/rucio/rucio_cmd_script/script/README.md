### istruzioni per gestione file con RUCIO ###
- collegarsi alla macchina di backend (notebook.cygno.cloud.infn.it)
- far partire la shell per varie applicazioni di script offline/RUCIO 
- se non e' gia' attivo (`myps` controllare che siano in esecuzione rucio-daq, tokener e tokener_tape) lanciare il docker compose
```
sudo su
cd middleware/conf/rucio/rucio_cmd_script/script/
docker compose up -d
```
- che fa partre la shell e i tokener per s3/tape, poi connettersi al docker 
```
docker attach rucio-daq
```
- se serve di accedere con gfal ai file del TAPE caricare il token ()
```
export BEARER_TOKEN=$(cat /tmp/token)
# controllare se tutto funziona con
gfal-ls davs://xfer-archive.cr.cnaf.infn.it:8443/cygno
```
### copia su TAPE e registrazione da S3 ####
ad esempio per controllare e compiare i file da S3 (bari) su TAPE
```
python3 copy_register_s3_to_tape.py --bucket cygno-data --prefix LNF/ --scope cygno-data --log_file register_to_tape_LNF_BA.log
```
per minio
```
python3 copy_register_s3_to_tape.py --bucket cygno-data --prefix LNF/ --scope cygno-data --minio --log_file register_to_tape_LNF_MINIO.log
```
se i file esistono su tape, o sono gia' registrati lo script non fa nulla (ovvero riscontrolla solamente); altrimenti se non sono registrati ma presenti, li registra; se non sono presenti li scarica e li copia sul tape e li registra. se vuoi copiare tuttto il bucket usare ''
```
python3 copy_register_s3_to_tape.py --bucket cygno-analysis --prefix '' --scope cygno-analysis --minio --log_file register_to_tape_analysis_MINIO.log
```
```
python3 copy_register_s3_to_tape.py --bucket cygno-sim --prefix '' --scope cygno-sim --minio --log_file register_to_tape_sim_MINIO.log
```
###replica i file tra 2 rse a partire da una lista
```
python3 replicate_files_source_to_dest.py --scope cygno-data --prefix LNGS --source_rse T1_USERTAPE --dest_rse CNAF_USERDISK --account rucio-daq   --file_list LNGS.txt --log_file replicate_files_LNGS.log
```
### Mostra tutti di did (data identyfier di una scope) che possono essere su varie RSE
- `rucio list-dids cygno-sim:"*" --filter type=FILE`
- `rucio list-dids cygno-data:'LNF/*' --filter type=FILE | wc` (per sapere quanti did sono impostati per uno specifico scope)

### Trovato il nome del did 
- `rucio list-file-replicas cygno-analysis:TRJ/SUB1/test-register-01` (ovvero il did)
- `rucio replica list file cygno-data:LNF/run13844.mid.gz`
- `rucio list-rules cygno-analysis:SGA/TRJ/test-cnaf-rse-01` (ovvero il did)
- `rucio rule list --did cygno-data:LNF/run13844.mid.gz`

Attenzione a gli apici!
```
RSE=T1_USERTAPE (esempio)
PREFIX='*' # 'LNF/*'
rucio list-dids ${SCOPE}:"${PREFIX}" --filter type=FILE | awk -F'|' 'NR>3 && NF>=2 { s=$2; gsub(/^[ \t]+|[ \t]+$/,"",s); if(s!="") print s }' > /tmp/files.txt
RID=$(rucio list-rules `tail -1 /tmp/files.txt` | awk -v rse="$RSE" 'NR>2 && $5 ~ rse {print $1}');
while read -r DID; do RID=$(rucio list-rules "$DID" | awk -v rse="$RSE" 'NR>2 && $5 ~ rse {print $1}'); rucio rule remove "$RID";   echo ">> $RID $DID REMOUVED!"; done < /tmp/files.txt
```

### replica file dal TAPE su CNAF_USERDISK
- `docker attach rucio-daq`
- se non si e' sicuri del path del file eventualemnte controllare lo stato del file by name, 
con il comando:
```
python3 find_file_in_rucio.py --filename run00143.mid.gz
```
e quindi trovare il did corretto che definira' anche dove il file verra' replicato.

- richidere di scaricare la replica su CNAF_USERDISK da T1_USERTAPE con il comando: 
```
# ricopia un file da tape a CNAF_USERDISK per 3 mesi, oppure mettere quello che si vuole o rimuovere
rucio rule add --copies 1 --rse-exp CNAF_USERDISK --lifetime 7776000 cygno-data:MAN/run26737.mid.gz
``` 
- fare eventualemnte una lista di file per un determinato TAG o di did e eseguire il loop:
```
while read fname; do rucio rule add --copies 1 --rse-exp CNAF_USERDISK cygno-data:TAG/$fname; done < list.txt
```  
- ricordarsi di disconnetrsi con la sequenza Crtl-P Ctrl-Q, e non con exit

