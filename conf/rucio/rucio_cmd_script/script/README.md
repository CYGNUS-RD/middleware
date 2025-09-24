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
