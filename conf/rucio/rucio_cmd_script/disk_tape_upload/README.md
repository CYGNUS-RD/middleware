imagine per upoload dati dal DAQ
- v0.3 controllo del "register_after_upload": True, eliminato il warning
- v0.2 controllo degli errori
- v0.1 base
```
docker build -t gmazzitelli/rucio-uploader:v0.X .
```
esempio di upload test2_14G.dat in nello spazio di FLASH
```
docker run --rm -v /home/.rucio.cfg:/home/.rucio.cfg -v ./test2_14G.dat:/app/test2_14G.dat gmazzitelli/rucio-uploader:v0.3 --file /app/test2_14G.dat --bucket cygno-data --did_name FLASH/QUAX/TEST/test2_14G.dat --upload_rse CNAF_USERDISK --transfer_rse T1_USERTAPE --account rucio-daq
```
