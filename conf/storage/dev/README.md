copia di una lista di file da minio a BARI
creare la lista con i filename filelist.txt nel formato:

...
run73878.mid.gz
run73879.mid.gz
...

ad esemio si puo' fare attraverso i comandi
'''
for i in seq 40784 1 40918; do echo run$i.mid.gz; done > filelist.txt
IFS=$'\n';for line in `cat filelist.txt`; do ./cp_minio2ba.py ${line} ; done
'''

il programma ./cp_minio2ba.py accetta anche bucket di ingresso e uscita e tag di ingresso uscida diversi
l'opzione -r cancella il file remoto
 
./ba_ls.py lista i file su BARI

questi 2 scipt operano su qualunque macchina linux che abbia le boto (le credenziali) e un tmp dove mettere il file temporaneo.

per sottomettere la copia come processo:
'''
IFS=$'\n';for line in cat filelist2.txt; do ./cp_minio2ba.py ${line} ; done >> ./tranfer2.log 2>&1 &
'''
lista i filename solo (o il campo che vuoi)
'''
./ba_ls.py | grep LNGS | awk '{print $1}' | cut -d "/" -f 2
'''
