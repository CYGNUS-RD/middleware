copia di una lista di file da minio a BARI
creare la lista con i filename filelist.txt nel formato:

...
run73878.mid.gz
run73879.mid.gz
...

eseguire il comando
'''
IFS=$'\n';for line in `cat filelist.txt`; do ./cp_minio2ba.py ${line} ; done
'''

il programma ./cp_minio2ba.py accetta anche bucket di ingresso e uscita e tag di ingresso uscida diversi
l'opzione -r cancella il file remoto
 
./ba_ls.py lista i file su BARI
