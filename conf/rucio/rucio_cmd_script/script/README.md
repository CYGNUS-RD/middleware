shell per varie applicazioni di script offline/RUCIO
lanciare il docker compose 
```docker compose up -d```

che fa partre la shell e i tokenr per s3/tape, poi connettersi al docker 
```docker attach rucio-shell```

caricare il tocken per gfal
```export BEARER_TOKEN=$(cat tape_token)```

### copy su TAPE e registrazione da S3 ####
ad esempio per controllare e compiare i file da S3 (bari) su TAPE
```python3 copy_register_s3_to_tape.py --bucket cygno-data --prefix LNF/ --scope cygno-data --log_file register_to_tape_LNF_BA.log```
per minio
```python3 copy_register_s3_to_tape.py --bucket cygno-data --prefix LNF/ --scope cygno-data --minio --log_file register_to_tape_LNF_MINIO.log```


se i file esistono su tape, o sono gia' registrati lo script non fa nulla (ovvero riscontrolla solamente);
altrimenti se non sono registrati ma presenti, li registra; se non sono presenti li scarica e li copia sul tape e li registra.

se vuoi copiare tuttto il bucket usare ''

python3 copy_register_s3_to_tape.py --bucket cygno-analysis --prefix '' --scope cygno-analysis --minio --log_file register_to_tape_analysis_MINIO.log
python3 copy_register_s3_to_tape.py --bucket cygno-sim --prefix '' --scope cygno-sim --minio --log_file register_to_tape_sim_MINIO.log

replica i file tra 2 rse a partire da una lista

python3 replicate_files_source_to_dest.py --scope cygno-data --prefix LNGS --source_rse T1_USERTAPE --dest_rse CNAF_USERDISK --account rucio-daq   --file_list LNGS.txt --log_file replicate_files_LNGS.log

Mostra tutti di did (data identyfier di una scope) che possono essere su varie RSE

rucio list-dids cygno-sim:"*" --filter type=FILE 
rucio list-dids cygno-data:'LNF/*' --filter type=FILE | wc (per sapere quanti did sono impostati per uno specifico scope)

Trovato il nome del did 
rucio list-file-replicas  cygno-analysis:TRJ/SUB1/test-register-01 (ovvero il did)
rucio replica list file cygno-data:LNF/run13844.mid.gz
rucio list-rules cygno-analysis:SGA/TRJ/test-cnaf-rse-01 (ovvero il did)
rucio rule list --did cygno-data:LNF/run13844.mid.gz


Attenzione a gli apici!
RSE=T1_USERTAPE (esempio)
PREFIX='*' # 'LNF/*'
rucio list-dids ${SCOPE}:"${PREFIX}" --filter type=FILE | awk -F'|' 'NR>3 && NF>=2 { s=$2; gsub(/^[ \t]+|[ \t]+$/,"",s); if(s!="") print s }' > /tmp/files.txt
RID=$(rucio list-rules `tail -1 /tmp/files.txt` | awk -v rse="$RSE" 'NR>2 && $5 ~ rse {print $1}');
while read -r DID; do RID=$(rucio list-rules "$DID" | awk -v rse="$RSE" 'NR>2 && $5 ~ rse {print $1}'); rucio rule remove "$RID";   echo ">> $RID $DID REMOUVED!"; done < /tmp/files.txt
