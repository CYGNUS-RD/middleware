questo docker e script fanno la replica su disco quello che e' sull tape

docker run --rm   -v $(pwd)/LNGS.txt:/app/LNGS.txt \
-v /root/.rucio.cfg:/home/.rucio.cfg   \
-v $(pwd)/replica_status.log:/app/replica_status.log   \
gmazzitelli/rucio-replicator:v0.1   \
--scope cygno-data   --prefix LNGS   --source_rse T1_USERTAPE   \
--dest_rse CNAF_USERDISK   --account rucio-daq   --file_list LNGS.txt
